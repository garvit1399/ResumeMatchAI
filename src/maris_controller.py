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
        context_for_scorer = {
            'resume_data': resume_data,
            'job_data': job_data
        }
        match_score_msg = self.match_scorer.process(
            {'resume_text': resume_text, 'job_text': job_text},
            context=context_for_scorer
        )
        match_score = match_score_msg.output
        
        # Step 4: Analyze skill gaps (with context)
        context_for_gap = {
            'resume_data': resume_data,
            'job_data': job_data
        }
        gap_analysis_msg = self.skill_gap_analyzer.process({}, context=context_for_gap)
        gap_analysis = gap_analysis_msg.output
        
        # Step 5: Verification (with all context)
        context_for_verification = {
            'resume_data': resume_data_msg,
            'job_data': job_data_msg,
            'match_score': match_score_msg,
            'gap_analysis': gap_analysis_msg
        }
        verification_msg = self.verification_agent.process(
            {'resume_text': resume_text, 'job_text': job_text},
            context=context_for_verification
        )
        verification = verification_msg.output
        
        # Compile comprehensive results
        results = {
            'final_score': verification.get('final_score', match_score.get('match_score', 0)),
            'confidence': verification.get('confidence', 'Medium'),
            'stability_index': verification.get('stability_index', 0.0),
            'verified': verification.get('verified', False),
            
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
            agent_name: agent.agent_role
            for agent_name, agent in self.agents.items()
        }
    
    def clear_all_history(self):
        """Clear message history from all agents."""
        for agent in self.agents.values():
            agent.clear_history()

