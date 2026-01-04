"""
Skill Gap & Recommendation Agent
Identifies missing skills, suggests learning paths, and ranks importance.
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentMessage


class SkillGapAgent(BaseAgent):
    """Agent specialized in identifying skill gaps and recommendations."""
    
    def __init__(self):
        """Initialize skill gap agent."""
        super().__init__("SkillGap")
    
    def process(self, input_data: Dict[str, Any]) -> AgentMessage:
        """
        Identify skill gaps and generate recommendations.
        
        Args:
            input_data: Dictionary with 'resume_data' and 'job_data' keys
            
        Returns:
            AgentMessage with skill gap analysis
        """
        resume_data = input_data.get('resume_data', {})
        job_data = input_data.get('job_data', {})
        
        if not resume_data or not job_data:
            return self.create_message(
                output={},
                confidence=0.0,
                reasoning="Missing resume or job data"
            )
        
        resume_skills = set(resume_data.get('skills', []))
        required_skills = set(job_data.get('required_skills', []))
        preferred_skills = set(job_data.get('preferred_skills', []))
        
        # Identify missing skills
        missing_required = required_skills - resume_skills
        missing_preferred = preferred_skills - resume_skills
        
        # Rank importance (required skills are more important)
        critical_skills = sorted(list(missing_required))
        nice_to_have = sorted(list(missing_preferred))
        
        # Calculate coverage
        total_required = len(required_skills)
        matching_required = len(resume_skills & required_skills)
        coverage = (matching_required / total_required * 100) if total_required > 0 else 100.0
        
        # Generate learning path suggestions
        learning_path = self._generate_learning_path(critical_skills)
        
        # Build output
        output = {
            'missing_required_skills': critical_skills,
            'missing_preferred_skills': nice_to_have,
            'matching_skills': sorted(list(resume_skills & required_skills)),
            'skill_coverage': round(coverage, 2),
            'total_required': total_required,
            'matching_count': matching_required,
            'learning_path': learning_path,
            'priority_skills': critical_skills[:5]  # Top 5 most critical
        }
        
        # Calculate confidence
        confidence = self._calculate_gap_confidence(output)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(output)
        
        # Collect evidence
        evidence = [
            f"Missing {len(critical_skills)} required skills",
            f"Missing {len(nice_to_have)} preferred skills",
            f"Skill coverage: {coverage:.1f}%",
            f"Top priority: {', '.join(critical_skills[:3])}" if critical_skills else "All skills present"
        ]
        
        return self.create_message(
            output=output,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
    
    def _generate_learning_path(self, missing_skills: List[str]) -> List[Dict[str, str]]:
        """Generate learning path suggestions."""
        # Simple learning path generation
        # In production, this would use a skill knowledge graph
        
        learning_path = []
        
        # Skill dependencies (simplified)
        skill_dependencies = {
            'machine learning': ['python', 'statistics', 'data analysis'],
            'deep learning': ['machine learning', 'python', 'neural networks'],
            'react': ['javascript', 'html', 'css'],
            'kubernetes': ['docker', 'linux', 'devops'],
            'aws': ['linux', 'networking', 'cloud computing']
        }
        
        for skill in missing_skills[:5]:  # Top 5
            skill_lower = skill.lower()
            prerequisites = []
            
            # Check for dependencies
            for key, deps in skill_dependencies.items():
                if key in skill_lower:
                    prerequisites = deps
                    break
            
            learning_path.append({
                'skill': skill,
                'prerequisites': prerequisites,
                'suggested_order': len(learning_path) + 1
            })
        
        return learning_path
    
    def _calculate_gap_confidence(self, output: Dict[str, Any]) -> float:
        """Calculate confidence in gap analysis."""
        confidence = 0.8  # Base confidence for gap analysis
        
        # More skills analyzed = higher confidence
        if output['total_required'] > 5:
            confidence += 0.1
        
        if output['total_required'] > 10:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_reasoning(self, output: Dict[str, Any]) -> str:
        """Generate reasoning summary."""
        parts = []
        
        parts.append(
            f"Identified {len(output['missing_required_skills'])} missing required skills "
            f"and {len(output['missing_preferred_skills'])} missing preferred skills."
        )
        
        parts.append(f"Skill coverage: {output['skill_coverage']:.1f}%.")
        
        if output['priority_skills']:
            parts.append(
                f"Top priority skills to learn: {', '.join(output['priority_skills'][:3])}."
            )
        
        return " ".join(parts)
