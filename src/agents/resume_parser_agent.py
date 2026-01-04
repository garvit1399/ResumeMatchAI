"""
Resume Parser Agent
Extracts structured information from resumes using NLP and rule-based extraction.
"""

import re
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentMessage
from ..skill_gap import SkillExtractor
from ..preprocess import TextPreprocessor


class ResumeParserAgent(BaseAgent):
    """Agent specialized in parsing and extracting structured data from resumes."""
    
    def __init__(self):
        """Initialize resume parser agent."""
        super().__init__("ResumeParser")
        self.skill_extractor = SkillExtractor()
        self.preprocessor = TextPreprocessor()
    
    def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """
        Parse resume and extract structured information.
        
        Args:
            input_data: Dictionary with 'resume_text' key
            
        Returns:
            AgentMessage with parsed resume data
        """
        resume_text = input_data.get('resume_text', '')
        
        if not resume_text:
            return self.create_message(
                output={},
                confidence=0.0,
                reasoning="No resume text provided"
            )
        
        # Extract entities
        entities = self.skill_extractor.extract_all(resume_text)
        
        # Extract experience years
        experience_years = self._extract_experience_years(resume_text)
        
        # Extract education level
        education_level = self._extract_education_level(resume_text)
        
        # Extract job titles/roles
        job_titles = self._extract_job_titles(resume_text)
        
        # Build structured output
        output = {
            'skills': sorted(list(entities['skills'])),
            'tools': sorted(list(entities['tools'])),
            'experience_years': experience_years,
            'education_level': education_level,
            'education_keywords': entities['education'],
            'job_titles': job_titles,
            'experience_keywords': entities['experience_keywords'],
            'total_skills': len(entities['skills']),
            'total_tools': len(entities['tools'])
        }
        
        # Calculate confidence
        confidence = self._calculate_parsing_confidence(output, resume_text)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(output)
        
        # Collect evidence
        evidence = [
            f"Extracted {len(output['skills'])} skills",
            f"Found {len(output['tools'])} tools",
            f"Estimated {experience_years} years of experience",
            f"Education level: {education_level}"
        ]
        
        return self.create_message(
            output=output,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
    
    def _extract_experience_years(self, text: str) -> float:
        """Extract years of experience from resume."""
        text_lower = text.lower()
        
        # Look for patterns like "5 years", "3+ years", etc.
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'(\d+)\+?\s*years?\s+in',
            r'(\d+)\+?\s*years?\s+of'
        ]
        
        years_found = []
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    years_found.append(float(match))
                except ValueError:
                    pass
        
        # Also look for date ranges
        date_pattern = r'(\d{4})\s*[-–]\s*(\d{4}|present|current)'
        date_matches = re.findall(date_pattern, text, re.IGNORECASE)
        
        if date_matches:
            # Rough estimate: assume 1 year per date range
            years_found.append(len(date_matches))
        
        if years_found:
            return max(years_found)  # Take maximum
        else:
            # Estimate based on job titles count
            job_titles = self._extract_job_titles(text)
            return min(len(job_titles) * 1.5, 10.0)  # Cap at 10
    
    def _extract_education_level(self, text: str) -> str:
        """Extract highest education level."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['phd', 'ph.d', 'doctorate', 'doctoral']):
            return 'PhD'
        elif any(word in text_lower for word in ['master', 'ms', 'ma', 'mba', 'mtech', 'msc']):
            return 'Masters'
        elif any(word in text_lower for word in ['bachelor', 'bs', 'ba', 'btech', 'bsc']):
            return 'Bachelors'
        elif any(word in text_lower for word in ['diploma', 'certification', 'certificate']):
            return 'Diploma/Certification'
        else:
            return 'Unknown'
    
    def _extract_job_titles(self, text: str) -> List[str]:
        """Extract job titles from resume."""
        # Simple pattern matching for common job titles
        # In production, this would use NER or more sophisticated extraction
        lines = text.split('\n')
        titles = []
        
        # Common title patterns
        title_keywords = [
                    'engineer', 'developer', 'analyst', 'manager', 'director',
            'specialist', 'consultant', 'architect', 'scientist', 'lead',
            'senior', 'junior', 'principal', 'staff'
        ]
        
        for line in lines[:20]:  # Check first 20 lines
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in title_keywords):
                # Clean up the line
                title = line.strip()
                if len(title) < 50 and len(title) > 5:
                    titles.append(title)
        
        return titles[:5]  # Return top 5
    
    def _calculate_parsing_confidence(
        self,
        output: Dict[str, Any],
        resume_text: str
    ) -> float:
        """Calculate confidence in parsing results."""
        confidence = 0.5  # Base confidence
        
        # More skills found = higher confidence
        if output['total_skills'] > 5:
            confidence += 0.2
        if output['total_skills'] > 10:
            confidence += 0.1
        
        # Experience years found
        if output['experience_years'] > 0:
            confidence += 0.1
        
        # Education level found
        if output['education_level'] != 'Unknown':
            confidence += 0.1
        
        # Job titles found
        if len(output['job_titles']) > 0:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, output: Dict[str, Any]) -> str:
        """Generate reasoning summary."""
        parts = []
        
        parts.append(f"Parsed resume with {output['total_skills']} skills and {output['total_tools']} tools.")
        
        if output['experience_years'] > 0:
            parts.append(f"Estimated {output['experience_years']} years of experience.")
        
        if output['education_level'] != 'Unknown':
            parts.append(f"Education level: {output['education_level']}.")
        
        if output['job_titles']:
            parts.append(f"Found {len(output['job_titles'])} job titles.")
        
        return " ".join(parts)
