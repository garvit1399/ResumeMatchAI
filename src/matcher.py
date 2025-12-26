"""
Matching Module
Computes similarity scores between resume and job description using embeddings.
"""

import numpy as np
from typing import Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity

from .embeddings import EmbeddingGenerator
from .skill_gap import SkillGapAnalyzer, SkillExtractor
from .preprocess import TextPreprocessor
from .explainable import ExplainableAnalyzer
from .skill_confidence import SkillConfidenceAnalyzer
from .ats_optimizer import ATSOptimizer
from .resume_rewriter import ResumeRewriter


class ResumeJobMatcher:
    """Main matching engine that combines all components."""
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        custom_skills: set = None
    ):
        """
        Initialize matcher.
        
        Args:
            embedding_model: Sentence transformer model name
            custom_skills: Additional custom skills to search for
        """
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.preprocessor = TextPreprocessor()
        self.skill_extractor = SkillExtractor(custom_skills)
        self.skill_gap_analyzer = SkillGapAnalyzer(self.skill_extractor)
        self.explainable_analyzer = ExplainableAnalyzer(self.skill_extractor)
        self.skill_confidence_analyzer = SkillConfidenceAnalyzer(self.skill_extractor)
        self.ats_optimizer = ATSOptimizer(self.skill_extractor)
        self.resume_rewriter = ResumeRewriter(self.skill_extractor, self.preprocessor)
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        emb1 = self.embedding_generator.encode(text1)
        emb2 = self.embedding_generator.encode(text2)
        
        # Reshape for cosine_similarity (needs 2D arrays)
        emb1 = emb1.reshape(1, -1)
        emb2 = emb2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def compute_section_scores(
        self,
        resume_text: str,
        job_text: str
    ) -> Dict[str, float]:
        """
        Compute similarity scores for different sections.
        
        Args:
            resume_text: Full resume text
            job_text: Full job description text
            
        Returns:
            Dictionary with section scores
        """
        # Preprocess texts
        resume_processed = self.preprocessor.preprocess(resume_text)
        job_processed = self.preprocessor.preprocess(job_text)
        
        # Overall semantic similarity
        overall_score = self.compute_similarity(resume_processed, job_processed)
        
        # Extract entities
        resume_entities = self.skill_extractor.extract_all(resume_text)
        job_entities = self.skill_extractor.extract_all(job_text)
        
        # Skills similarity
        resume_skills_text = " ".join(resume_entities['skills'])
        job_skills_text = " ".join(job_entities['skills'])
        skill_score = self.compute_similarity(resume_skills_text, job_skills_text) if job_skills_text else 0.0
        
        # Tools similarity
        resume_tools_text = " ".join(resume_entities['tools'])
        job_tools_text = " ".join(job_entities['tools'])
        tool_score = self.compute_similarity(resume_tools_text, job_tools_text) if job_tools_text else 0.0
        
        # Experience keywords similarity
        resume_exp_text = " ".join(resume_entities['experience_keywords'])
        job_exp_text = " ".join(job_entities['experience_keywords'])
        experience_score = self.compute_similarity(resume_exp_text, job_exp_text) if job_exp_text else 0.0
        
        # Education similarity (binary/overlap based)
        resume_edu = set(resume_entities['education'])
        job_edu = set(job_entities['education'])
        if job_edu:
            education_score = len(resume_edu & job_edu) / len(job_edu)
        else:
            education_score = 1.0  # No education requirement
        
        return {
            'overall': overall_score,
            'skills': skill_score,
            'tools': tool_score,
            'experience': experience_score,
            'education': education_score
        }
    
    def compute_weighted_score(
        self,
        resume_text: str,
        job_text: str,
        weights: Dict[str, float] = None
    ) -> Dict[str, any]:
        """
        Compute weighted match score with skill gap analysis.
        
        Args:
            resume_text: Full resume text
            job_text: Full job description text
            weights: Dictionary with section weights
                     Default: skills=0.4, experience=0.3, education=0.15, tools=0.15
            
        Returns:
            Dictionary with comprehensive matching results
        """
        if weights is None:
            weights = {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.15,
                'tools': 0.15
            }
        
        # Validate weights sum to 1.0
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        # Get section scores
        section_scores = self.compute_section_scores(resume_text, job_text)
        
        # Compute weighted score
        weighted_score = (
            section_scores['skills'] * weights['skills'] +
            section_scores['experience'] * weights['experience'] +
            section_scores['education'] * weights['education'] +
            section_scores['tools'] * weights['tools']
        )
        
        # Normalize to 0-100
        match_score = weighted_score * 100
        
        # Skill gap analysis
        gap_analysis = self.skill_gap_analyzer.analyze_gap(resume_text, job_text)
        
        # Explainable AI analysis
        explanations = self.explainable_analyzer.analyze_score_breakdown(
            resume_text, job_text, section_scores, weights
        )
        top_reasons = self.explainable_analyzer.get_top_reasons_low_score(match_score, explanations)
        resume_highlights = self.explainable_analyzer.highlight_resume_sections(resume_text, job_text)
        
        # Skill confidence analysis
        skill_confidence = self.skill_confidence_analyzer.analyze_skill_confidence(resume_text)
        skill_strength_summary = self.skill_confidence_analyzer.get_skill_strength_summary(skill_confidence)
        
        # ATS optimization analysis
        ats_analysis = self.ats_optimizer.analyze_ats_compatibility(resume_text, job_text)
        ats_recommendations = self.ats_optimizer.get_ats_recommendations(ats_analysis)
        
        # Resume rewrite suggestions
        rewrite_suggestions = self.resume_rewriter.suggest_rewrites(resume_text, job_text)
        
        return {
            'match_score': round(match_score, 2),
            'overall_similarity': round(section_scores['overall'] * 100, 2),
            'section_scores': {
                'skills': round(section_scores['skills'] * 100, 2),
                'experience': round(section_scores['experience'] * 100, 2),
                'education': round(section_scores['education'] * 100, 2),
                'tools': round(section_scores['tools'] * 100, 2)
            },
            'weights': weights,
            'gap_analysis': gap_analysis,
            'explanations': explanations,
            'top_reasons_low_score': top_reasons,
            'resume_highlights': resume_highlights,
            'skill_confidence': skill_confidence,
            'skill_strength_summary': skill_strength_summary,
            'ats_analysis': ats_analysis,
            'ats_recommendations': ats_recommendations,
            'rewrite_suggestions': rewrite_suggestions
        }
    
    def match(
        self,
        resume_text: str,
        job_text: str,
        weights: Dict[str, float] = None
    ) -> Dict[str, any]:
        """
        Main matching function - alias for compute_weighted_score.
        
        Args:
            resume_text: Full resume text
            job_text: Full job description text
            weights: Dictionary with section weights
            
        Returns:
            Dictionary with comprehensive matching results
        """
        return self.compute_weighted_score(resume_text, job_text, weights)

