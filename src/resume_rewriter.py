"""
Resume Rewrite Suggestions Module
Suggests improvements to resume bullet points to better match job descriptions.
"""

import re
from typing import Dict, List, Tuple
from .skill_gap import SkillExtractor
from .preprocess import TextPreprocessor


class ResumeRewriter:
    """Suggests resume rewrites to better match job descriptions."""
    
    # Action verb templates for stronger impact
    ACTION_VERB_TEMPLATES = {
        'improved': ['optimized', 'enhanced', 'streamlined', 'refined'],
        'worked': ['developed', 'implemented', 'designed', 'built'],
        'helped': ['contributed to', 'supported', 'facilitated', 'enabled'],
        'did': ['executed', 'delivered', 'achieved', 'accomplished'],
        'made': ['created', 'established', 'founded', 'initiated']
    }
    
    def __init__(self, skill_extractor: SkillExtractor, preprocessor: TextPreprocessor):
        """
        Initialize resume rewriter.
        
        Args:
            skill_extractor: SkillExtractor instance
            preprocessor: TextPreprocessor instance
        """
        self.skill_extractor = skill_extractor
        self.preprocessor = preprocessor
    
    def suggest_rewrites(
        self,
        resume_text: str,
        job_text: str,
        max_suggestions: int = 5
    ) -> List[Dict[str, str]]:
        """
        Suggest rewrites for resume bullet points.
        
        Args:
            resume_text: Resume text
            job_text: Job description text
            max_suggestions: Maximum number of suggestions
            
        Returns:
            List of rewrite suggestions
        """
        suggestions = []
        
        # Extract job keywords and skills
        job_entities = self.skill_extractor.extract_all(job_text)
        job_skills = job_entities['skills']
        job_keywords = set(job_entities['experience_keywords'])
        
        # Split resume into sentences/bullet points
        # Look for bullet points (lines starting with -, •, or numbered)
        lines = resume_text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Check if it's a bullet point
            if re.match(r'^[-•*]\s+', line) or re.match(r'^\d+[.)]\s+', line):
                bullet_points.append(line)
            elif len(line) > 20 and len(line) < 200:  # Potential bullet point
                bullet_points.append(line)
        
        # Analyze each bullet point
        for bullet in bullet_points[:20]:  # Limit analysis
            bullet_lower = bullet.lower()
            
            # Check if bullet contains job skills
            bullet_skills = self.skill_extractor.extract_skills(bullet)
            matching_skills = bullet_skills & job_skills
            
            # Check for weak verbs
            weak_verbs_found = []
            for weak_verb, strong_alternatives in self.ACTION_VERB_TEMPLATES.items():
                if re.search(r'\b' + weak_verb + r'\b', bullet_lower):
                    weak_verbs_found.append((weak_verb, strong_alternatives))
            
            # Generate suggestions
            if matching_skills or weak_verbs_found:
                suggestion = {
                    'original': bullet[:150] + '...' if len(bullet) > 150 else bullet,
                    'suggested': self._generate_rewrite(bullet, job_skills, weak_verbs_found),
                    'reason': self._get_suggestion_reason(bullet, matching_skills, weak_verbs_found)
                }
                suggestions.append(suggestion)
        
        return suggestions[:max_suggestions]
    
    def _generate_rewrite(
        self,
        original: str,
        job_skills: set,
        weak_verbs: List[Tuple[str, List[str]]]
    ) -> str:
        """
        Generate a suggested rewrite.
        
        Args:
            original: Original bullet point
            job_skills: Job-relevant skills
            weak_verbs: List of (weak_verb, alternatives) tuples
            
        Returns:
            Suggested rewrite
        """
        rewritten = original
        
        # Replace weak verbs with stronger alternatives
        for weak_verb, alternatives in weak_verbs:
            pattern = r'\b' + re.escape(weak_verb) + r'\b'
            if alternatives:
                # Use first alternative (could be randomized)
                rewritten = re.sub(pattern, alternatives[0], rewritten, flags=re.IGNORECASE)
        
        # Add missing job skills if relevant (simple approach)
        # In a real implementation, this would use more sophisticated NLP
        bullet_skills = self.skill_extractor.extract_skills(original)
        missing_skills = job_skills - bullet_skills
        
        if missing_skills and len(original) < 100:
            # Try to naturally incorporate a missing skill
            skill_to_add = list(missing_skills)[0]
            if skill_to_add not in rewritten.lower():
                # Simple addition (real implementation would be more sophisticated)
                rewritten = rewritten.rstrip('.') + f" using {skill_to_add}."
        
        return rewritten
    
    def _get_suggestion_reason(
        self,
        bullet: str,
        matching_skills: set,
        weak_verbs: List[Tuple[str, List[str]]]
    ) -> str:
        """Get reason for suggestion."""
        reasons = []
        
        if weak_verbs:
            reasons.append(f"Use stronger action verbs (e.g., {weak_verbs[0][1][0]})")
        
        if matching_skills:
            reasons.append(f"Already mentions relevant skills: {', '.join(list(matching_skills)[:2])}")
        else:
            reasons.append("Could emphasize job-relevant skills more")
        
        return "; ".join(reasons)

