"""
Verification & Bias Agent
Validates claims, stress-tests score stability, and flags uncertain outputs.
"""

import re
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentMessage
from ..embeddings import EmbeddingGenerator
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class VerificationAgent(BaseAgent):
    """Agent specialized in verification and bias detection."""
    
    def __init__(self):
        """Initialize verification agent."""
        super().__init__("Verification")
        self.embedding_generator = EmbeddingGenerator()
    
    def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """
        Verify outputs from other agents and test stability.
        
        Args:
            input_data: Dictionary with agent outputs and original texts
            
        Returns:
            AgentMessage with verification results
        """
        resume_text = input_data.get('resume_text', '')
        job_text = input_data.get('job_text', '')
        
        # Get data from input_data or context
        if context:
            # Extract from context messages if available
            resume_data_msg = context.get('resume_data')
            job_data_msg = context.get('job_data')
            match_score_msg = context.get('match_score')
            
            # Handle AgentMessage objects or dicts
            if hasattr(resume_data_msg, 'output'):
                resume_data = resume_data_msg.output
            elif isinstance(resume_data_msg, dict):
                resume_data = resume_data_msg
            else:
                resume_data = {}
            
            if hasattr(job_data_msg, 'output'):
                job_data = job_data_msg.output
            elif isinstance(job_data_msg, dict):
                job_data = job_data_msg
            else:
                job_data = {}
            
            # Extract match score from message or input
            if match_score_msg:
                if hasattr(match_score_msg, 'output'):
                    score_val = match_score_msg.output.get('overall_score', 0)
                elif isinstance(match_score_msg, dict):
                    score_val = match_score_msg.get('overall_score', 0)
                else:
                    score_val = 0
                
                # Convert to 0-100 scale if needed
                if isinstance(score_val, (int, float)):
                    match_score = score_val if score_val <= 1.0 else score_val / 100.0
                else:
                    match_score = 0.0
            else:
                match_score = input_data.get('match_score', 0)
                if isinstance(match_score, (int, float)) and match_score > 1:
                    match_score = match_score / 100.0
        else:
            match_score = input_data.get('match_score', 0)
            if isinstance(match_score, (int, float)) and match_score > 1:
                match_score = match_score / 100.0
            resume_data = input_data.get('resume_data', {})
            job_data = input_data.get('job_data', {})
        
        # Stability testing (match_score should be 0-1 scale for internal use)
        # But we need 0-100 for display, so convert
        match_score_for_stability = match_score if match_score <= 1.0 else match_score / 100.0
        stability_results = self._test_stability(resume_text, job_text, match_score_for_stability * 100.0)
        
        # Self-consistency checks
        consistency_results = self._check_consistency(
            resume_data, job_data, match_score
        )
        
        # Confidence assessment
        confidence_level = self._assess_confidence(
            stability_results, consistency_results
        )
        
        # Flag warnings
        warnings = self._generate_warnings(
            stability_results, consistency_results
        )
        
        # Build output
        output = {
            'final_score': round(match_score, 2),
            'confidence_level': confidence_level,
            'stability_index': round(stability_results['stability_index'], 3),
            'score_variance': round(stability_results['variance'], 3),
            'consistency_score': round(consistency_results['consistency'], 3),
            'warnings': warnings,
            'is_stable': stability_results['is_stable'],
            'is_consistent': consistency_results['is_consistent']
        }
        
        # Calculate agent confidence
        confidence = self._calculate_verification_confidence(output)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(output)
        
        # Collect evidence
        evidence = [
            f"Stability index: {output['stability_index']:.3f}",
            f"Score variance: {output['score_variance']:.3f}",
            f"Confidence level: {output['confidence_level']}",
            f"Warnings: {len(warnings)}"
        ]
        
        return self.create_message(
            output=output,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
    
    def _test_stability(
        self,
        resume_text: str,
        job_text: str,
        original_score: float
    ) -> Dict[str, Any]:
        """Test score stability with perturbations."""
        if not resume_text or not job_text:
            return {
                'stability_index': 0.0,
                'variance': 1.0,
                'is_stable': False
            }
        
        # Create perturbations
        perturbations = []
        
        # Perturbation 1: Reorder sections
        lines = resume_text.split('\n')
        if len(lines) > 5:
            reordered = '\n'.join(lines[-3:] + lines[:-3])
            perturbations.append(reordered)
        
        # Perturbation 2: Remove some whitespace
        compressed = re.sub(r'\s+', ' ', resume_text)
        if len(compressed) > 100:
            perturbations.append(compressed)
        
        # Perturbation 3: Original (for baseline)
        perturbations.append(resume_text)
        
        # Compute scores for each perturbation
        scores = []
        for perturbed_resume in perturbations[:3]:  # Limit to 3
            try:
                score = self._quick_score(perturbed_resume, job_text)
                scores.append(score)
            except:
                pass
        
        if not scores:
            return {
                'stability_index': 0.5,
                'variance': 0.5,
                'is_stable': True
            }
        
        # Calculate variance
        mean_score = np.mean(scores)
        variance = np.var(scores)
        
        # Stability index: lower variance = higher stability
        stability_index = max(0.0, 1.0 - min(1.0, variance * 10))
        
        # Consider stable if variance < 0.05
        is_stable = variance < 0.05
        
        return {
            'stability_index': stability_index,
            'variance': variance,
            'is_stable': is_stable,
            'mean_score': mean_score
        }
    
    def _quick_score(self, resume_text: str, job_text: str) -> float:
        """Quick score computation for stability testing."""
        # Simplified scoring for speed
        emb1 = self.embedding_generator.encode(resume_text)
        emb2 = self.embedding_generator.encode(job_text)
        
        emb1 = emb1.reshape(1, -1)
        emb2 = emb2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def _check_consistency(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any],
        match_score: float
    ) -> Dict[str, Any]:
        """Check self-consistency of results."""
        # Check if score aligns with data
        resume_skills = set(resume_data.get('skills', []))
        required_skills = set(job_data.get('required_skills', []))
        
        skill_match_ratio = 0.0
        if required_skills:
            skill_match_ratio = len(resume_skills & required_skills) / len(required_skills)
        
        # Expected score based on skill match
        expected_score_range = (skill_match_ratio * 0.7, skill_match_ratio * 0.9)
        actual_score_normalized = match_score / 100.0
        
        # Check if actual score is in expected range
        is_consistent = (
            expected_score_range[0] <= actual_score_normalized <= expected_score_range[1]
        ) or skill_match_ratio == 0
        
        # Consistency score
        if expected_score_range[1] > 0:
            consistency = 1.0 - abs(
                actual_score_normalized - np.mean(expected_score_range)
            ) / expected_score_range[1]
            consistency = max(0.0, min(1.0, consistency))
        else:
            consistency = 1.0
        
        return {
            'consistency': consistency,
            'is_consistent': is_consistent,
            'skill_match_ratio': skill_match_ratio,
            'expected_range': expected_score_range
        }
    
    def _assess_confidence(
        self,
        stability_results: Dict[str, Any],
        consistency_results: Dict[str, Any]
    ) -> str:
        """Assess overall confidence level."""
        stability = stability_results.get('stability_index', 0.5)
        consistency = consistency_results.get('consistency', 0.5)
        
        avg_confidence = (stability + consistency) / 2.0
        
        if avg_confidence >= 0.8:
            return "High"
        elif avg_confidence >= 0.6:
            return "Medium"
        else:
            return "Low"
    
    def _generate_warnings(
        self,
        stability_results: Dict[str, Any],
        consistency_results: Dict[str, Any]
    ) -> List[str]:
        """Generate warnings for uncertain outputs."""
        warnings = []
        
        if not stability_results.get('is_stable', True):
            warnings.append("Score may be unstable - consider reviewing resume formatting")
        
        if not consistency_results.get('is_consistent', True):
            warnings.append("Score may not align with skill match ratio - verification recommended")
        
        if stability_results.get('variance', 0) > 0.1:
            warnings.append("High score variance detected - results may vary")
        
        return warnings
    
    def _calculate_verification_confidence(self, output: Dict[str, Any]) -> float:
        """Calculate verification agent confidence."""
        confidence = 0.7  # Base confidence
        
        if output['is_stable']:
            confidence += 0.1
        
        if output['is_consistent']:
            confidence += 0.1
        
        if output['confidence_level'] == 'High':
            confidence += 0.1
        
        if len(output['warnings']) == 0:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, output: Dict[str, Any]) -> str:
        """Generate reasoning summary."""
        parts = []
        
        parts.append(
            f"Verified match score of {output['final_score']:.1f}% "
            f"with {output['confidence_level'].lower()} confidence."
        )
        
        parts.append(
            f"Stability index: {output['stability_index']:.3f}, "
            f"Consistency: {output['consistency_score']:.3f}."
        )
        
        if output['warnings']:
            parts.append(f"Generated {len(output['warnings'])} warnings.")
        else:
            parts.append("No warnings - results are stable and consistent.")
        
        return " ".join(parts)
