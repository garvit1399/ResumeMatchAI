"""
Skill & Entity Extraction Module
Extracts skills, tools, education, and experience keywords from text.
"""

import re
from typing import List, Set, Dict, Tuple
from collections import Counter

# Common technical skills database
TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'rust',
    'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'sql', 'html', 'css',
    'perl', 'shell', 'bash', 'powershell',
    
    # Frameworks & Libraries
    'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi', 'spring',
    'express', 'laravel', 'rails', 'tensorflow', 'pytorch', 'keras', 'scikit-learn',
    'pandas', 'numpy', 'matplotlib', 'seaborn',
    
    # Databases
    'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite',
    'cassandra', 'dynamodb', 'neo4j',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
    'terraform', 'ansible', 'linux', 'unix',
    
    # Tools & Platforms
    'git', 'github', 'gitlab', 'jira', 'confluence', 'slack', 'tableau', 'power bi',
    'excel', 'sas', 'spss', 'splunk', 'databricks', 'snowflake',
    
    # Methodologies
    'agile', 'scrum', 'kanban', 'devops', 'mlops', 'microservices', 'rest api',
    'graphql', 'api development',
    
    # Data Science & ML
    'machine learning', 'deep learning', 'neural networks', 'nlp', 'computer vision',
    'data analysis', 'data visualization', 'statistics', 'a/b testing',
    
    # Other
    'project management', 'leadership', 'communication', 'problem solving'
}

# Education keywords
EDUCATION_KEYWORDS = {
    'bachelor', 'master', 'phd', 'doctorate', 'degree', 'diploma', 'certification',
    'bs', 'ba', 'ms', 'ma', 'mba', 'ph.d', 'bsc', 'msc', 'mtech', 'btech'
}

# Experience keywords
EXPERIENCE_KEYWORDS = {
    'years', 'experience', 'worked', 'developed', 'implemented', 'managed',
    'led', 'created', 'designed', 'built', 'maintained', 'optimized',
    'engineered', 'architected', 'deployed', 'delivered'
}

# Tools & Technologies (additional to technical skills)
TOOLS_KEYWORDS = {
    'jira', 'confluence', 'slack', 'teams', 'zoom', 'tableau', 'power bi',
    'excel', 'word', 'powerpoint', 'outlook', 'salesforce', 'hubspot'
}


class SkillExtractor:
    """Extracts skills, education, tools, and experience from text."""
    
    def __init__(self, custom_skills: Set[str] = None):
        """
        Initialize skill extractor.
        
        Args:
            custom_skills: Additional custom skills to search for
        """
        self.all_skills = TECHNICAL_SKILLS.copy()
        if custom_skills:
            self.all_skills.update(s.lower() for s in custom_skills)
    
    def extract_skills(self, text: str) -> Set[str]:
        """
        Extract technical skills from text.
        
        Args:
            text: Input text (preprocessed or raw)
            
        Returns:
            Set of found skills
        """
        if not text:
            return set()
        
        text_lower = text.lower()
        found_skills = set()
        
        # Check for each skill in the text
        for skill in self.all_skills:
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        return found_skills
    
    def extract_education(self, text: str) -> List[str]:
        """
        Extract education-related keywords.
        
        Args:
            text: Input text
            
        Returns:
            List of education keywords found
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found = []
        
        for keyword in EDUCATION_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                found.append(keyword)
        
        return found
    
    def extract_experience_keywords(self, text: str) -> List[str]:
        """
        Extract experience-related keywords.
        
        Args:
            text: Input text
            
        Returns:
            List of experience keywords found
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found = []
        
        for keyword in EXPERIENCE_KEYWORDS:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower):
                found.append(keyword)
        
        return found
    
    def extract_tools(self, text: str) -> Set[str]:
        """
        Extract tools and technologies.
        
        Args:
            text: Input text
            
        Returns:
            Set of found tools
        """
        if not text:
            return set()
        
        text_lower = text.lower()
        found_tools = set()
        
        # Check technical skills (many are tools)
        found_tools.update(self.extract_skills(text))
        
        # Check additional tool keywords
        for tool in TOOLS_KEYWORDS:
            pattern = r'\b' + re.escape(tool) + r'\b'
            if re.search(pattern, text_lower):
                found_tools.add(tool)
        
        return found_tools
    
    def extract_all(self, text: str) -> Dict[str, any]:
        """
        Extract all entities: skills, education, experience, tools.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with extracted entities
        """
        return {
            'skills': self.extract_skills(text),
            'education': self.extract_education(text),
            'experience_keywords': self.extract_experience_keywords(text),
            'tools': self.extract_tools(text)
        }


class SkillGapAnalyzer:
    """Analyzes skill gaps between resume and job description."""
    
    def __init__(self, skill_extractor: SkillExtractor = None):
        """
        Initialize analyzer.
        
        Args:
            skill_extractor: SkillExtractor instance (creates new if None)
        """
        self.skill_extractor = skill_extractor or SkillExtractor()
    
    def analyze_gap(self, resume_text: str, job_text: str) -> Dict[str, any]:
        """
        Analyze skill gap between resume and job description.
        
        Args:
            resume_text: Resume text
            job_text: Job description text
            
        Returns:
            Dictionary with gap analysis results
        """
        resume_entities = self.skill_extractor.extract_all(resume_text)
        job_entities = self.skill_extractor.extract_all(job_text)
        
        resume_skills = resume_entities['skills']
        job_skills = job_entities['skills']
        
        resume_tools = resume_entities['tools']
        job_tools = job_entities['tools']
        
        # Find missing skills
        missing_skills = job_skills - resume_skills
        matching_skills = job_skills & resume_skills
        
        # Find missing tools
        missing_tools = job_tools - resume_tools
        matching_tools = job_tools & resume_tools
        
        # Calculate coverage
        skill_coverage = len(matching_skills) / len(job_skills) * 100 if job_skills else 0
        tool_coverage = len(matching_tools) / len(job_tools) * 100 if job_tools else 0
        
        return {
            'missing_skills': sorted(missing_skills),
            'matching_skills': sorted(matching_skills),
            'missing_tools': sorted(missing_tools),
            'matching_tools': sorted(matching_tools),
            'skill_coverage': round(skill_coverage, 2),
            'tool_coverage': round(tool_coverage, 2),
            'resume_skills': sorted(resume_skills),
            'job_skills': sorted(job_skills),
            'resume_education': resume_entities['education'],
            'job_education': job_entities['education'],
            'resume_experience_keywords': resume_entities['experience_keywords'],
            'job_experience_keywords': job_entities['experience_keywords']
        }

