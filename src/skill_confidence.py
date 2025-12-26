"""
Skill Confidence Scoring Module
Detects strength of skill usage (strong/moderate/weak) based on context, verbs, and recency.
"""

import re
from typing import Dict, List, Tuple
from collections import Counter
from .skill_gap import SkillExtractor


class SkillConfidenceAnalyzer:
    """Analyzes confidence/strength of skills in resume."""
    
    # Strong action verbs that indicate deep experience
    STRONG_VERBS = {
        'architected', 'designed', 'built', 'developed', 'implemented', 'created',
        'engineered', 'optimized', 'led', 'managed', 'established', 'founded',
        'transformed', 'improved', 'enhanced', 'deployed', 'scaled', 'migrated'
    }
    
    # Moderate action verbs
    MODERATE_VERBS = {
        'worked', 'used', 'utilized', 'applied', 'assisted', 'contributed',
        'participated', 'collaborated', 'supported', 'helped', 'involved'
    }
    
    # Experience indicators
    EXPERIENCE_INDICATORS = {
        'years', 'year', 'months', 'month', 'experience', 'experienced',
        'proficient', 'expert', 'advanced', 'senior', 'lead', 'principal'
    }
    
    def __init__(self, skill_extractor: SkillExtractor):
        """
        Initialize skill confidence analyzer.
        
        Args:
            skill_extractor: SkillExtractor instance
        """
        self.skill_extractor = skill_extractor
    
    def analyze_skill_confidence(
        self,
        resume_text: str,
        skills: List[str] = None
    ) -> Dict[str, Dict[str, any]]:
        """
        Analyze confidence level for each skill.
        
        Args:
            resume_text: Resume text
            skills: List of skills to analyze (if None, extracts from resume)
            
        Returns:
            Dictionary mapping skill to confidence data
        """
        if skills is None:
            entities = self.skill_extractor.extract_all(resume_text)
            skills = list(entities['skills'])
        
        skill_confidence = {}
        
        # Split resume into sentences
        sentences = re.split(r'[.!?]+\s+', resume_text)
        resume_lower = resume_text.lower()
        
        for skill in skills:
            skill_lower = skill.lower()
            confidence_data = {
                'skill': skill,
                'mentions': 0,
                'contexts': [],
                'verbs': [],
                'experience_level': 'weak',
                'confidence': 'weak'
            }
            
            # Count mentions
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            mentions = len(re.findall(pattern, resume_lower))
            confidence_data['mentions'] = mentions
            
            # Find sentences containing the skill
            skill_sentences = [s for s in sentences if re.search(pattern, s.lower())]
            
            # Analyze verbs in those sentences
            for sentence in skill_sentences:
                sentence_lower = sentence.lower()
                # Check for strong verbs
                for verb in self.STRONG_VERBS:
                    if re.search(r'\b' + verb + r'\b', sentence_lower):
                        confidence_data['verbs'].append(verb)
                        break
                # Check for moderate verbs
                for verb in self.MODERATE_VERBS:
                    if re.search(r'\b' + verb + r'\b', sentence_lower):
                        confidence_data['verbs'].append(verb)
                        break
                
                # Check for experience indicators
                for indicator in self.EXPERIENCE_INDICATORS:
                    if re.search(r'\b' + indicator + r'\b', sentence_lower):
                        confidence_data['contexts'].append(indicator)
            
            # Determine confidence level
            strong_verb_count = sum(1 for v in confidence_data['verbs'] if v in self.STRONG_VERBS)
            moderate_verb_count = sum(1 for v in confidence_data['verbs'] if v in self.MODERATE_VERBS)
            has_experience_indicator = len(confidence_data['contexts']) > 0
            
            if mentions >= 3 and strong_verb_count >= 2:
                confidence_data['confidence'] = 'strong'
                confidence_data['experience_level'] = 'strong'
            elif mentions >= 2 and (strong_verb_count >= 1 or has_experience_indicator):
                confidence_data['confidence'] = 'moderate'
                confidence_data['experience_level'] = 'moderate'
            elif mentions >= 1:
                confidence_data['confidence'] = 'moderate'
                confidence_data['experience_level'] = 'moderate'
            else:
                confidence_data['confidence'] = 'weak'
                confidence_data['experience_level'] = 'weak'
            
            skill_confidence[skill] = confidence_data
        
        return skill_confidence
    
    def get_skill_strength_summary(
        self,
        skill_confidence: Dict[str, Dict[str, any]]
    ) -> Dict[str, List[str]]:
        """
        Get summary of skill strengths.
        
        Args:
            skill_confidence: Skill confidence dictionary
            
        Returns:
            Dictionary with strong, moderate, and weak skills
        """
        summary = {
            'strong': [],
            'moderate': [],
            'weak': []
        }
        
        for skill, data in skill_confidence.items():
            confidence = data['confidence']
            summary[confidence].append(skill)
        
        return summary

