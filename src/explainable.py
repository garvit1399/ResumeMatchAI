"""
Explainable AI Module
Provides detailed explanations for match scores, highlighting what helped or hurt.
"""

import re
from typing import Dict, List, Tuple
from collections import Counter
from .skill_gap import SkillExtractor


class ExplainableAnalyzer:
    """Analyzes and explains match scores with detailed breakdowns."""
    
    def __init__(self, skill_extractor: SkillExtractor):
        """
        Initialize explainable analyzer.
        
        Args:
            skill_extractor: SkillExtractor instance
        """
        self.skill_extractor = skill_extractor
    
    def analyze_score_breakdown(
        self,
        resume_text: str,
        job_text: str,
        section_scores: Dict[str, float],
        weights: Dict[str, float]
    ) -> Dict[str, any]:
        """
        Analyze why the score is what it is.
        
        Args:
            resume_text: Resume text
            job_text: Job description text
            section_scores: Section scores (0-1 scale)
            weights: Section weights
            
        Returns:
            Dictionary with explanations
        """
        explanations = {
            'top_strengths': [],
            'top_weaknesses': [],
            'section_impact': {},
            'missing_critical_skills': [],
            'strong_matches': [],
            'score_breakdown': {}
        }
        
        # Calculate section impact on final score
        for section, score in section_scores.items():
            if section == 'overall':
                continue
            weight = weights.get(section, 0)
            impact = score * weight * 100  # Contribution to final score
            explanations['section_impact'][section] = {
                'score': round(score * 100, 2),
                'weight': round(weight * 100, 2),
                'contribution': round(impact, 2),
                'status': 'strong' if score > 0.7 else 'moderate' if score > 0.4 else 'weak'
            }
        
        # Extract entities for detailed analysis
        resume_entities = self.skill_extractor.extract_all(resume_text)
        job_entities = self.skill_extractor.extract_all(job_text)
        
        # Find strong matches
        matching_skills = set(resume_entities['skills']) & set(job_entities['skills'])
        if matching_skills:
            explanations['strong_matches'] = sorted(list(matching_skills))[:10]
        
        # Find missing critical skills
        missing_skills = set(job_entities['skills']) - set(resume_entities['skills'])
        if missing_skills:
            explanations['missing_critical_skills'] = sorted(list(missing_skills))[:10]
        
        # Identify top strengths
        strengths = []
        for section, data in explanations['section_impact'].items():
            if data['status'] == 'strong':
                strengths.append({
                    'section': section,
                    'message': f"Strong {section} match ({data['score']:.1f}%)"
                })
        explanations['top_strengths'] = strengths[:5]
        
        # Identify top weaknesses
        weaknesses = []
        for section, data in explanations['section_impact'].items():
            if data['status'] == 'weak':
                impact_loss = (1.0 - section_scores[section]) * weights[section] * 100
                weaknesses.append({
                    'section': section,
                    'message': f"{section.capitalize()} section reduces score by {impact_loss:.1f}%",
                    'impact': round(impact_loss, 2)
                })
        # Sort by impact
        weaknesses.sort(key=lambda x: x['impact'], reverse=True)
        explanations['top_weaknesses'] = weaknesses[:5]
        
        # Score breakdown
        total_contribution = sum(data['contribution'] for data in explanations['section_impact'].values())
        explanations['score_breakdown'] = {
            'total_contribution': round(total_contribution, 2),
            'sections': explanations['section_impact']
        }
        
        return explanations
    
    def get_top_reasons_low_score(
        self,
        match_score: float,
        explanations: Dict[str, any]
    ) -> List[str]:
        """
        Get top 5 reasons why score is low.
        
        Args:
            match_score: Overall match score (0-100)
            explanations: Explanation dictionary
            
        Returns:
            List of reason strings
        """
        reasons = []
        
        if match_score < 50:
            # Low score reasons
            if explanations['missing_critical_skills']:
                top_missing = explanations['missing_critical_skills'][:3]
                reasons.append(f"❌ Missing critical skills: {', '.join(top_missing)}")
            
            for weakness in explanations['top_weaknesses'][:3]:
                reasons.append(f"📉 {weakness['message']}")
            
            # Check for low section scores
            for section, data in explanations['section_impact'].items():
                if data['score'] < 30:
                    reasons.append(f"⚠️ Very low {section} match ({data['score']:.1f}%)")
        
        return reasons[:5]
    
    def highlight_resume_sections(
        self,
        resume_text: str,
        job_text: str
    ) -> Dict[str, List[str]]:
        """
        Highlight which resume sections helped or hurt the score.
        
        Args:
            resume_text: Resume text
            job_text: Job description text
            
        Returns:
            Dictionary with helpful and hurtful sections
        """
        # Simple section detection
        sections = {
            'experience': [],
            'education': [],
            'skills': [],
            'summary': []
        }
        
        # Extract job keywords
        job_entities = self.skill_extractor.extract_all(job_text)
        job_skills = set(job_entities['skills'])
        job_keywords = set(job_entities['experience_keywords'])
        
        # Split resume into sentences
        sentences = re.split(r'[.!?]+\s+', resume_text)
        
        helpful = []
        hurtful = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            # Check if sentence contains job skills
            sentence_skills = self.skill_extractor.extract_skills(sentence)
            matching = sentence_skills & job_skills
            
            if matching:
                helpful.append({
                    'text': sentence.strip()[:100] + '...' if len(sentence) > 100 else sentence.strip(),
                    'reason': f"Contains matching skills: {', '.join(list(matching)[:3])}"
                })
            elif any(kw in sentence_lower for kw in ['lack', 'no experience', 'not familiar', 'limited']):
                hurtful.append({
                    'text': sentence.strip()[:100] + '...' if len(sentence) > 100 else sentence.strip(),
                    'reason': "Contains negative language"
                })
        
        return {
            'helpful': helpful[:5],
            'hurtful': hurtful[:3]
        }

