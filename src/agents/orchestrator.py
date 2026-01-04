"""
Multi-Agent Orchestrator
Coordinates agent communication and workflow execution.
"""

from typing import Dict, List, Any, Optional
from .base_agent import AgentMessage
from .resume_parser_agent import ResumeParserAgent
from .job_analyzer_agent import JobAnalyzerAgent
from .match_scoring_agent import MatchScoringAgent
from .skill_gap_agent import SkillGapAgent
from .verification_agent import VerificationAgent
import time


class AgentOrchestrator:
    """Orchestrates multi-agent workflow for resume-job matching."""
    
    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.resume_parser = ResumeParserAgent()
        self.job_analyzer = JobAnalyzerAgent()
        self.match_scorer = MatchScoringAgent()
        self.skill_gap = SkillGapAgent()
        self.verification = VerificationAgent()
        
        self.agent_messages = []
    
    def run_pipeline(
        self,
        resume_text: str,
        job_text: str
    ) -> Dict[str, Any]:
        """
        Run the complete multi-agent pipeline.
        
        Args:
            resume_text: Resume text
            job_text: Job description text
            
        Returns:
            Dictionary with all agent outputs and final results
        """
        self.agent_messages = []
        start_time = time.time()
        
        # Step 1: Parse Resume
        resume_message = self.resume_parser.process({
            'resume_text': resume_text
        })
        self.agent_messages.append(resume_message)
        resume_data = resume_message.output
        
        # Step 2: Analyze Job
        job_message = self.job_analyzer.process({
            'job_text': job_text
        })
        self.agent_messages.append(job_message)
        job_data = job_message.output
        
        # Step 3: Compute Match Score
        match_message = self.match_scorer.process({
            'resume_data': resume_data,
            'job_data': job_data,
            'resume_text': resume_text,
            'job_text': job_text
        })
        self.agent_messages.append(match_message)
        match_score = match_message.output.get('overall_score', 0)
        
        # Step 4: Identify Skill Gaps
        gap_message = self.skill_gap.process({
            'resume_data': resume_data,
            'job_data': job_data
        })
        self.agent_messages.append(gap_message)
        
        # Step 5: Verify Results
        verification_message = self.verification.process({
            'resume_text': resume_text,
            'job_text': job_text,
            'match_score': match_score,
            'resume_data': resume_data,
            'job_data': job_data
        })
        self.agent_messages.append(verification_message)
        
        elapsed_time = time.time() - start_time
        
        # Aggregate results
        results = {
            'resume_data': resume_data,
            'job_data': job_data,
            'match_score': match_score,
            'gap_analysis': gap_message.output,
            'verification': verification_message.output,
            'section_scores': match_message.output.get('section_scores', {}),
            'agent_messages': [msg.to_dict() for msg in self.agent_messages],
            'agent_contributions': self._calculate_agent_contributions(),
            'pipeline_metadata': {
                'elapsed_time': round(elapsed_time, 2),
                'agent_count': len(self.agent_messages),
                'average_confidence': self._calculate_average_confidence()
            }
        }
        
        return results
    
    def _calculate_agent_contributions(self) -> Dict[str, float]:
        """Calculate how much each agent influenced the final score."""
        contributions = {}
        
        # Find match scoring agent
        match_msg = next(
            (msg for msg in self.agent_messages if msg.agent == "MatchScoring"),
            None
        )
        
        if match_msg:
            section_scores = match_msg.output.get('section_scores', {})
            weights = match_msg.output.get('weights', {})
            
            for section, weight in weights.items():
                score = section_scores.get(section, 0) / 100.0
                contributions[section] = round(score * weight * 100, 2)
        
        return contributions
    
    def _calculate_average_confidence(self) -> float:
        """Calculate average confidence across all agents."""
        if not self.agent_messages:
            return 0.0
        
        total_confidence = sum(msg.confidence for msg in self.agent_messages)
        return round(total_confidence / len(self.agent_messages), 3)
    
    def get_agent_reasoning(self) -> Dict[str, str]:
        """Get reasoning from all agents."""
        reasoning = {}
        for msg in self.agent_messages:
            if msg.reasoning:
                reasoning[msg.agent] = msg.reasoning
        return reasoning
    
    def get_agent_evidence(self) -> Dict[str, List[str]]:
        """Get evidence from all agents."""
        evidence = {}
        for msg in self.agent_messages:
            if msg.evidence:
                evidence[msg.agent] = msg.evidence
        return evidence

