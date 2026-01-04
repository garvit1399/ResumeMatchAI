"""
Match Scoring Agent
Computes fit score by aggregating signals from other agents.
"""

from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentMessage
from ..embeddings import EmbeddingGenerator
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class MatchScoringAgent(BaseAgent):
    """Agent specialized in computing match scores."""
    
    def __init__(self):
        """Initialize match scoring agent."""
        super().__init__("MatchScoring")
        self.embedding_generator = EmbeddingGenerator()
    
    def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """
        Compute match score from resume and job data.
        
        Args:
            input_data: Dictionary with 'resume_data' and 'job_data' keys
            
        Returns:
            AgentMessage with match scores
        """
        # Get data from input_data or context
        resume_data = input_data.get('resume_data') or (context.get('resume_data', {}) if context else {})
        job_data = input_data.get('job_data') or (context.get('job_data', {}) if context else {})
        resume_text = input_data.get('resume_text', '')
        job_text = input_data.get('job_text', '')
        
        if not resume_data or not job_data:
            return self.create_message(
                output={},
                confidence=0.0,
                reasoning="Missing resume or job data"
            )
        
        # Compute section scores
        skill_score = self._compute_skill_score(resume_data, job_data)
        experience_score = self._compute_experience_score(resume_data, job_data)
        education_score = self._compute_education_score(resume_data, job_data)
        tool_score = self._compute_tool_score(resume_data, job_data)
        
        # Compute semantic similarity if texts available
        semantic_score = 0.0
        if resume_text and job_text:
            semantic_score = self._compute_semantic_similarity(resume_text, job_text)
        
        # Weighted overall score
        weights = {
            'skills': 0.4,
            'experience': 0.3,
            'education': 0.15,
            'tools': 0.15
        }
        
        weighted_score = (
            skill_score * weights['skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education'] +
            tool_score * weights['tools']
        )
        
        # Build output
        output = {
            'overall_score': round(weighted_score * 100, 2),
            'semantic_similarity': round(semantic_score * 100, 2),
            'section_scores': {
                'skills': round(skill_score * 100, 2),
                'experience': round(experience_score * 100, 2),
                'education': round(education_score * 100, 2),
                'tools': round(tool_score * 100, 2)
            },
            'weights': weights,
            'skill_match_count': len(
                set(resume_data.get('skills', [])) &
                set(job_data.get('required_skills', []))
            ),
            'total_required_skills': len(job_data.get('required_skills', []))
        }
        
        # Calculate confidence
        confidence = self._calculate_scoring_confidence(output, resume_data, job_data)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(output)
        
        # Collect evidence
        evidence = [
            f"Skill match: {output['skill_match_count']}/{output['total_required_skills']}",
            f"Overall score: {output['overall_score']:.1f}%",
            f"Semantic similarity: {output['semantic_similarity']:.1f}%"
        ]
        
        return self.create_message(
            output=output,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
    
    def _compute_skill_score(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """Compute skill matching score."""
        resume_skills = set(resume_data.get('skills', []))
        required_skills = set(job_data.get('required_skills', []))
        preferred_skills = set(job_data.get('preferred_skills', []))
        
        if not required_skills and not preferred_skills:
            return 1.0  # No requirements = perfect match
        
        # Required skills are weighted more
        required_match = len(resume_skills & required_skills)
        preferred_match = len(resume_skills & preferred_skills)
        
        required_score = required_match / len(required_skills) if required_skills else 0.0
        preferred_score = preferred_match / len(preferred_skills) if preferred_skills else 0.0
        
        # Weighted combination: 70% required, 30% preferred
        if required_skills or preferred_skills:
            total_skills = len(required_skills) + len(preferred_skills)
            if total_skills > 0:
                score = (required_match * 0.7 + preferred_match * 0.3) / (
                    len(required_skills) * 0.7 + len(preferred_skills) * 0.3
                )
                return min(1.0, score)
        
        return 0.0
    
    def _compute_experience_score(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """Compute experience matching score."""
        resume_years = resume_data.get('experience_years', 0)
        required_years = job_data.get('experience_required', 0)
        
        if required_years == 0:
            return 1.0  # No requirement = perfect match
        
        if resume_years >= required_years:
            return 1.0
        else:
            # Partial credit for having some experience
            return min(1.0, resume_years / required_years)
    
    def _compute_education_score(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """Compute education matching score."""
        resume_edu = resume_data.get('education_level', 'Unknown')
        required_edu = job_data.get('education_required', 'Not Specified')
        
        if required_edu == 'Not Specified':
            return 1.0
        
        # Education hierarchy
        edu_hierarchy = {
            'Unknown': 0,
            'Diploma/Certification': 1,
            'Bachelors': 2,
            'Masters': 3,
            'PhD': 4
        }
        
        resume_level = edu_hierarchy.get(resume_edu, 0)
        required_level = edu_hierarchy.get(required_edu, 0)
        
        if resume_level >= required_level:
            return 1.0
        else:
            # Partial credit
            return max(0.0, resume_level / required_level) if required_level > 0 else 0.0
    
    def _compute_tool_score(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """Compute tool matching score."""
        resume_tools = set(resume_data.get('tools', []))
        job_tools = set(job_data.get('tools', []))
        
        if not job_tools:
            return 1.0
        
        match_count = len(resume_tools & job_tools)
        return min(1.0, match_count / len(job_tools))
    
    def _compute_semantic_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity using embeddings."""
        if not text1 or not text2:
            return 0.0
        
        emb1 = self.embedding_generator.encode(text1)
        emb2 = self.embedding_generator.encode(text2)
        
        emb1 = emb1.reshape(1, -1)
        emb2 = emb2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def _calculate_scoring_confidence(
        self,
        output: Dict[str, Any],
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence in scoring."""
        confidence = 0.7  # Base confidence
        
        # More data = higher confidence
        if output['total_required_skills'] > 0:
            confidence += 0.1
        
        if output['semantic_similarity'] > 0:
            confidence += 0.1
        
        # Skill match ratio
        if output['total_required_skills'] > 0:
            match_ratio = output['skill_match_count'] / output['total_required_skills']
            if match_ratio > 0.5:
                confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, output: Dict[str, Any]) -> str:
        """Generate reasoning summary."""
        parts = []
        
        parts.append(
            f"Computed overall match score of {output['overall_score']:.1f}% "
            f"based on weighted section scores."
        )
        
        parts.append(
            f"Skills: {output['section_scores']['skills']:.1f}%, "
            f"Experience: {output['section_scores']['experience']:.1f}%, "
            f"Education: {output['section_scores']['education']:.1f}%, "
            f"Tools: {output['section_scores']['tools']:.1f}%."
        )
        
        if output['semantic_similarity'] > 0:
            parts.append(
                f"Semantic similarity: {output['semantic_similarity']:.1f}%."
            )
        
        return " ".join(parts)
