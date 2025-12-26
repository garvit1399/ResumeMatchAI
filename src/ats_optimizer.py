"""
ATS (Applicant Tracking System) Optimization Module
Detects ATS-unfriendly formatting and suggests improvements.
"""

import re
from typing import Dict, List, Tuple
from .skill_gap import SkillExtractor


class ATSOptimizer:
    """Analyzes resume for ATS compatibility and suggests improvements."""
    
    # Standard section headers that ATS systems recognize
    STANDARD_HEADERS = {
        'experience', 'work experience', 'employment', 'professional experience',
        'education', 'academic background', 'qualifications',
        'skills', 'technical skills', 'core competencies',
        'summary', 'professional summary', 'objective', 'profile',
        'certifications', 'certificates', 'awards', 'achievements',
        'projects', 'publications', 'languages'
    }
    
    # ATS-unfriendly elements
    UNFRIENDLY_ELEMENTS = {
        'tables': r'<table|<tr|<td',
        'images': r'<img|\.jpg|\.png|\.gif',
        'columns': r'column|multicolumn',
        'headers_footers': r'header|footer',
        'text_boxes': r'text box|textbox'
    }
    
    def __init__(self, skill_extractor: SkillExtractor):
        """
        Initialize ATS optimizer.
        
        Args:
            skill_extractor: SkillExtractor instance
        """
        self.skill_extractor = skill_extractor
    
    def analyze_ats_compatibility(
        self,
        resume_text: str,
        job_text: str = None
    ) -> Dict[str, any]:
        """
        Analyze resume for ATS compatibility.
        
        Args:
            resume_text: Resume text
            job_text: Optional job description for keyword analysis
            
        Returns:
            Dictionary with ATS analysis results
        """
        analysis = {
            'ats_score': 0,
            'issues': [],
            'suggestions': [],
            'missing_sections': [],
            'keyword_placement': {},
            'formatting_issues': []
        }
        
        resume_lower = resume_text.lower()
        issues = []
        suggestions = []
        
        # Check for standard section headers
        found_headers = set()
        for header in self.STANDARD_HEADERS:
            pattern = r'\b' + re.escape(header) + r'\b'
            if re.search(pattern, resume_lower):
                found_headers.add(header)
        
        # Check for missing critical sections
        critical_sections = ['experience', 'education', 'skills']
        missing_sections = []
        for section in critical_sections:
            section_found = any(header in found_headers for header in self.STANDARD_HEADERS if section in header)
            if not section_found:
                missing_sections.append(section)
                issues.append(f"Missing '{section}' section header")
                suggestions.append(f"Add a clear '{section.capitalize()}' section header")
        
        analysis['missing_sections'] = missing_sections
        
        # Check for ATS-unfriendly formatting (basic text analysis)
        # Note: Full formatting detection would require PDF parsing
        
        # Check keyword placement
        if job_text:
            job_entities = self.skill_extractor.extract_all(job_text)
            job_skills = job_entities['skills']
            
            # Check if job keywords appear in resume
            resume_entities = self.skill_extractor.extract_all(resume_text)
            resume_skills = resume_entities['skills']
            
            missing_keywords = job_skills - resume_skills
            if missing_keywords:
                suggestions.append(
                    f"Consider adding these job keywords: {', '.join(list(missing_keywords)[:5])}"
                )
            
            # Check keyword frequency
            keyword_placement = {}
            for skill in job_skills:
                if skill in resume_skills:
                    # Count mentions
                    pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                    count = len(re.findall(pattern, resume_text.lower()))
                    keyword_placement[skill] = {
                        'present': True,
                        'mentions': count,
                        'recommendation': 'good' if count >= 2 else 'increase'
                    }
                else:
                    keyword_placement[skill] = {
                        'present': False,
                        'mentions': 0,
                        'recommendation': 'add'
                    }
            
            analysis['keyword_placement'] = keyword_placement
        
        # Calculate ATS score (0-100)
        score = 100
        score -= len(missing_sections) * 20  # -20 per missing section
        score -= len(issues) * 5  # -5 per issue
        score = max(0, min(100, score))
        
        analysis['ats_score'] = score
        analysis['issues'] = issues
        analysis['suggestions'] = suggestions
        
        return analysis
    
    def get_ats_recommendations(
        self,
        analysis: Dict[str, any]
    ) -> List[str]:
        """
        Get prioritized ATS recommendations.
        
        Args:
            analysis: ATS analysis dictionary
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Critical issues first
        if analysis['missing_sections']:
            recommendations.append(
                f"⚠️ CRITICAL: Add missing sections: {', '.join(analysis['missing_sections'])}"
            )
        
        # Keyword suggestions
        if analysis['keyword_placement']:
            missing = [k for k, v in analysis['keyword_placement'].items() if not v['present']]
            if missing:
                recommendations.append(
                    f"📝 Add these keywords: {', '.join(missing[:5])}"
                )
        
        # Formatting suggestions
        if analysis['suggestions']:
            recommendations.extend(analysis['suggestions'][:3])
        
        return recommendations

