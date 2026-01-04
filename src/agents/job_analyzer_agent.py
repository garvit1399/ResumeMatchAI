"""
Job Requirement Analyzer Agent
Identifies required vs preferred skills, experience level, and role expectations.
"""

import re
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentMessage
from ..skill_gap import SkillExtractor


class JobAnalyzerAgent(BaseAgent):
    """Agent specialized in analyzing job requirements."""
    
    def __init__(self):
        """Initialize job analyzer agent."""
        super().__init__("JobAnalyzer")
        self.skill_extractor = SkillExtractor()
    
    def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """
        Analyze job description and extract requirements.
        
        Args:
            input_data: Dictionary with 'job_text' key
            
        Returns:
            AgentMessage with analyzed job requirements
        """
        job_text = input_data.get('job_text', '')
        
        if not job_text:
            return self.create_message(
                output={},
                confidence=0.0,
                reasoning="No job description provided"
            )
        
        # Extract entities
        entities = self.skill_extractor.extract_all(job_text)
        
        # Categorize skills as required vs preferred
        required_skills, preferred_skills = self._categorize_skills(
            job_text, entities['skills']
        )
        
        # Extract experience requirements
        experience_required = self._extract_experience_requirement(job_text)
        
        # Extract education requirements
        education_required = self._extract_education_requirement(job_text, entities['education'])
        
        # Identify role level
        role_level = self._identify_role_level(job_text)
        
        # Build structured output
        output = {
            'required_skills': sorted(list(required_skills)),
            'preferred_skills': sorted(list(preferred_skills)),
            'all_skills': sorted(list(entities['skills'])),
            'tools': sorted(list(entities['tools'])),
            'experience_required': experience_required,
            'education_required': education_required,
            'role_level': role_level,
            'experience_keywords': entities['experience_keywords'],
            'total_required_skills': len(required_skills),
            'total_preferred_skills': len(preferred_skills)
        }
        
        # Calculate confidence
        confidence = self._calculate_analysis_confidence(output)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(output)
        
        # Collect evidence
        evidence = [
            f"Identified {len(required_skills)} required skills",
            f"Found {len(preferred_skills)} preferred skills",
            f"Role level: {role_level}",
            f"Experience required: {experience_required} years"
        ]
        
        return self.create_message(
            output=output,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
    
    def _categorize_skills(
        self,
        job_text: str,
        all_skills: set
    ) -> tuple:
        """Categorize skills as required vs preferred."""
        job_lower = job_text.lower()
        required = set()
        preferred = set()
        
        # Keywords that indicate required skills
        required_indicators = [
            'required', 'must have', 'must possess', 'essential',
            'mandatory', 'necessary', 'need', 'needs'
        ]
        
        # Keywords that indicate preferred skills
        preferred_indicators = [
            'preferred', 'nice to have', 'bonus', 'plus',
            'advantageous', 'desirable', 'optional'
        ]
        
        # Check context around each skill
        for skill in all_skills:
            skill_lower = skill.lower()
            # Find skill mentions in text
            pattern = r'\b' + skill_lower.replace('+', r'\+') + r'\b'
            matches = list(re.finditer(pattern, job_lower))
            
            if not matches:
                # Default to preferred if no context
                preferred.add(skill)
                continue
            
            # Check context around each mention
            is_required = False
            is_preferred = False
            
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(job_lower), match.end() + 50)
                context = job_lower[start:end]
                
                # Check for required indicators
                if any(indicator in context for indicator in required_indicators):
                    is_required = True
                    break
                
                # Check for preferred indicators
                if any(indicator in context for indicator in preferred_indicators):
                    is_preferred = True
            
            if is_required:
                required.add(skill)
            elif is_preferred:
                preferred.add(skill)
            else:
                # Default: if mentioned multiple times, likely required
                if len(matches) > 1:
                    required.add(skill)
                else:
                    preferred.add(skill)
        
        return required, preferred
    
    def _extract_experience_requirement(self, job_text: str) -> float:
        """Extract required years of experience."""
        text_lower = job_text.lower()
        
        # Patterns for experience requirements
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'minimum\s+of\s+(\d+)\s*years?',
            r'at\s+least\s+(\d+)\s*years?',
            r'(\d+)\+?\s*years?\s+in'
        ]
        
        years_found = []
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    years_found.append(float(match))
                except ValueError:
                    pass
        
        if years_found:
            return min(years_found)  # Take minimum requirement
        else:
            return 0.0
    
    def _extract_education_requirement(
        self,
        job_text: str,
        education_keywords: List[str]
    ) -> str:
        """Extract education requirement."""
        text_lower = job_text.lower()
        
        if any(word in text_lower for word in ['phd', 'ph.d', 'doctorate']):
            return 'PhD'
        elif any(word in text_lower for word in ['master', 'ms', 'ma', 'mba']):
            return 'Masters'
        elif any(word in text_lower for word in ['bachelor', 'bs', 'ba', 'degree']):
            return 'Bachelors'
        else:
            return 'Not Specified'
    
    def _identify_role_level(self, job_text: str) -> str:
        """Identify role level (Junior, Mid, Senior, etc.)."""
        text_lower = job_text.lower()
        
        if any(word in text_lower for word in ['senior', 'sr.', 'lead', 'principal', 'staff']):
            return 'Senior'
        elif any(word in text_lower for word in ['junior', 'jr.', 'entry', 'entry-level']):
            return 'Junior'
        elif any(word in text_lower for word in ['mid', 'mid-level', 'intermediate']):
            return 'Mid-Level'
        else:
            return 'Not Specified'
    
    def _calculate_analysis_confidence(self, output: Dict[str, Any]) -> float:
        """Calculate confidence in analysis."""
        confidence = 0.5  # Base confidence
        
        # More skills identified = higher confidence
        if output['total_required_skills'] > 3:
            confidence += 0.2
        if output['total_required_skills'] > 5:
            confidence += 0.1
        
        # Experience requirement found
        if output['experience_required'] > 0:
            confidence += 0.1
        
        # Education requirement found
        if output['education_required'] != 'Not Specified':
            confidence += 0.1
        
        # Role level identified
        if output['role_level'] != 'Not Specified':
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, output: Dict[str, Any]) -> str:
        """Generate reasoning summary."""
        parts = []
        
        parts.append(
            f"Analyzed job requirements: {output['total_required_skills']} required skills, "
            f"{output['total_preferred_skills']} preferred skills."
        )
        
        if output['experience_required'] > 0:
            parts.append(f"Requires {output['experience_required']} years of experience.")
        
        if output['education_required'] != 'Not Specified':
            parts.append(f"Education requirement: {output['education_required']}.")
        
        if output['role_level'] != 'Not Specified':
            parts.append(f"Role level: {output['role_level']}.")
        
        return " ".join(parts)
