"""
Multi-Job Comparison Module
Compare one resume against multiple job descriptions and rank them.
"""

from typing import Dict, List, Tuple
from .matcher import ResumeJobMatcher


class MultiJobComparator:
    """Compares one resume against multiple job descriptions."""
    
    def __init__(self, matcher: ResumeJobMatcher = None):
        """
        Initialize multi-job comparator.
        
        Args:
            matcher: ResumeJobMatcher instance (creates new if None)
        """
        self.matcher = matcher or ResumeJobMatcher()
    
    def compare_multiple_jobs(
        self,
        resume_text: str,
        job_descriptions: Dict[str, str],
        weights: Dict[str, float] = None
    ) -> List[Dict[str, any]]:
        """
        Compare resume against multiple job descriptions.
        
        Args:
            resume_text: Resume text
            job_descriptions: Dictionary mapping job title/ID to job description text
            weights: Optional custom weights for scoring
            
        Returns:
            List of comparison results, sorted by match score (highest first)
        """
        results = []
        
        for job_id, job_text in job_descriptions.items():
            # Get match results
            match_result = self.matcher.match(resume_text, job_text, weights)
            
            # Add job identifier
            match_result['job_id'] = job_id
            match_result['job_title'] = job_id  # Can be customized
            
            results.append(match_result)
        
        # Sort by match score (descending)
        results.sort(key=lambda x: x['match_score'], reverse=True)
        
        return results
    
    def get_best_fit_jobs(
        self,
        comparison_results: List[Dict[str, any]],
        top_n: int = 5
    ) -> List[Dict[str, any]]:
        """
        Get top N best-fit jobs.
        
        Args:
            comparison_results: Results from compare_multiple_jobs
            top_n: Number of top jobs to return
            
        Returns:
            List of top N jobs
        """
        return comparison_results[:top_n]
    
    def get_job_rankings(
        self,
        comparison_results: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Get detailed ranking analysis.
        
        Args:
            comparison_results: Results from compare_multiple_jobs
            
        Returns:
            Dictionary with ranking statistics
        """
        if not comparison_results:
            return {}
        
        scores = [r['match_score'] for r in comparison_results]
        
        return {
            'total_jobs': len(comparison_results),
            'average_score': sum(scores) / len(scores),
            'highest_score': max(scores),
            'lowest_score': min(scores),
            'score_range': max(scores) - min(scores),
            'top_job': comparison_results[0] if comparison_results else None,
            'rankings': [
                {
                    'rank': i + 1,
                    'job_id': r['job_id'],
                    'score': r['match_score'],
                    'skill_coverage': r['gap_analysis']['skill_coverage']
                }
                for i, r in enumerate(comparison_results)
            ]
        }
    
    def get_comparison_summary(
        self,
        comparison_results: List[Dict[str, any]]
    ) -> Dict[str, any]:
        """
        Get summary comparison across all jobs.
        
        Args:
            comparison_results: Results from compare_multiple_jobs
            
        Returns:
            Summary dictionary
        """
        if not comparison_results:
            return {}
        
        # Aggregate skill gaps
        all_missing_skills = set()
        all_matching_skills = set()
        
        for result in comparison_results:
            gap = result['gap_analysis']
            all_missing_skills.update(gap['missing_skills'])
            all_matching_skills.update(gap['matching_skills'])
        
        # Find most common missing skills
        missing_skill_counts = {}
        for result in comparison_results:
            for skill in result['gap_analysis']['missing_skills']:
                missing_skill_counts[skill] = missing_skill_counts.get(skill, 0) + 1
        
        most_common_missing = sorted(
            missing_skill_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            'total_jobs_compared': len(comparison_results),
            'average_match_score': sum(r['match_score'] for r in comparison_results) / len(comparison_results),
            'best_match_score': comparison_results[0]['match_score'] if comparison_results else 0,
            'worst_match_score': comparison_results[-1]['match_score'] if comparison_results else 0,
            'most_common_missing_skills': [skill for skill, count in most_common_missing],
            'universal_matching_skills': list(all_matching_skills),
            'universal_missing_skills': list(all_missing_skills)
        }

