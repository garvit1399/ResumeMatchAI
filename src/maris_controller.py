"""
MARIS Controller - Multi-Agent Resume Intelligence System Orchestrator
Coordinates multiple specialized agents to analyze resumes and job descriptions.
"""

from typing import Dict, Any, Optional
from .agents import (
    ResumeParserAgent,
    JobAnalyzerAgent,
    MatchScoringAgent,
    SkillGapAgent,
    VerificationAgent
)


class MARISController:
    """
    Multi-Agent Resume Intelligence System Controller.
    
    Orchestrates specialized AI agents to collaboratively analyze resumes
    and job descriptions with verification and explainability.
    """
    
    def __init__(self):
        """Initialize MARIS controller with all agents."""
        self.resume_parser = ResumeParserAgent()
        self.job_analyzer = JobAnalyzerAgent()
        self.match_scorer = MatchScoringAgent()
        self.skill_gap_analyzer = SkillGapAgent()
        self.verification_agent = VerificationAgent()
        
        self.agents = {
            'resume_parser': self.resume_parser,
            'job_analyzer': self.job_analyzer,
            'match_scorer': self.match_scorer,
            'skill_gap_analyzer': self.skill_gap_analyzer,
            'verification_agent': self.verification_agent
        }
    
    def run_pipeline(
        self,
        resume_text: str,
        job_text: str,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Run the complete MARIS pipeline.
        
        Args:
            resume_text: Resume text
            job_text: Job description text
            weights: Optional custom weights for scoring
            
        Returns:
            Comprehensive analysis results from all agents
        """
        # Step 1: Parse resume
        resume_data_msg = self.resume_parser.process({'resume_text': resume_text})
        resume_data = resume_data_msg.output
        
        # Step 2: Analyze job requirements
        job_data_msg = self.job_analyzer.process({'job_text': job_text})
        job_data = job_data_msg.output
        
        # Step 3: Compute match score (with context from previous agents)
        match_score_msg = self.match_scorer.process({
            'resume_data': resume_data,
            'job_data': job_data,
            'resume_text': resume_text,
            'job_text': job_text
        })
        match_score = match_score_msg.output
        
        # Step 4: Analyze skill gaps (with context)
        gap_analysis_msg = self.skill_gap_analyzer.process({
            'resume_data': resume_data,
            'job_data': job_data
        })
        gap_analysis = gap_analysis_msg.output
        
        # Step 5: Verification (with all context)
        # Extract match score (could be overall_score or match_score)
        overall_score = match_score.get('overall_score', 0)
        if isinstance(overall_score, (int, float)) and overall_score > 1:
            # If score is 0-100, convert to 0-1 for verification
            match_score_value = overall_score / 100.0
        else:
            match_score_value = overall_score if isinstance(overall_score, (int, float)) else 0.0
        
        verification_msg = self.verification_agent.process({
            'resume_text': resume_text,
            'job_text': job_text,
            'match_score': match_score_value * 100.0,  # Verification expects 0-100 scale
            'resume_data': resume_data,
            'job_data': job_data
        })
        verification = verification_msg.output
        
        # Compile comprehensive results
        # Get final score from verification or match_score
        final_score = verification.get('final_score', match_score.get('overall_score', 0))
        if not final_score or final_score == 0:
            final_score = match_score.get('overall_score', 0)
        
        results = {
            'final_score': final_score,
            'confidence': verification.get('confidence_level', 'Medium'),
            'stability_index': verification.get('stability_index', 0.0),
            'verified': verification.get('is_stable', False) and verification.get('is_consistent', False),
            
            # Agent outputs
            'resume_data': resume_data,
            'job_data': job_data,
            'match_score': match_score,
            'gap_analysis': gap_analysis,
            'verification': verification,
            
            # Agent messages (for explainability)
            'agent_messages': {
                'resume_parser': resume_data_msg.to_dict(),
                'job_analyzer': job_data_msg.to_dict(),
                'match_scorer': match_score_msg.to_dict(),
                'skill_gap_analyzer': gap_analysis_msg.to_dict(),
                'verification_agent': verification_msg.to_dict()
            },
            
            # Agent-level metrics
            'agent_metrics': {
                'resume_parser_confidence': resume_data_msg.confidence,
                'job_analyzer_confidence': job_data_msg.confidence,
                'match_scorer_confidence': match_score_msg.confidence,
                'skill_gap_analyzer_confidence': gap_analysis_msg.confidence,
                'verification_agent_confidence': verification_msg.confidence,
                'agent_agreement': verification.get('agent_agreement', 0)
            },
            
            # Warnings and issues
            'warnings': verification.get('warnings', []),
            
            # Explainability data
            'explainability': {
                'agent_reasoning': {
                    'resume_parser': resume_data_msg.reasoning,
                    'job_analyzer': job_data_msg.reasoning,
                    'match_scorer': match_score_msg.reasoning,
                    'skill_gap_analyzer': gap_analysis_msg.reasoning,
                    'verification_agent': verification_msg.reasoning
                },
                'agent_evidence': {
                    'resume_parser': resume_data_msg.evidence,
                    'job_analyzer': job_data_msg.evidence,
                    'match_scorer': match_score_msg.evidence,
                    'skill_gap_analyzer': gap_analysis_msg.evidence,
                    'verification_agent': verification_msg.evidence
                }
            }
        }
        
        return results
    
    def get_agent_summary(self) -> Dict[str, str]:
        """Get summary of all agents and their roles."""
        return {
            'resume_parser': 'Extracts structured information from resumes',
            'job_analyzer': 'Analyzes job requirements and categorizes skills',
            'match_scorer': 'Computes fit scores using multiple signals',
            'skill_gap_analyzer': 'Identifies missing skills and suggests learning paths',
            'verification_agent': 'Validates outputs and tests stability'
        }

