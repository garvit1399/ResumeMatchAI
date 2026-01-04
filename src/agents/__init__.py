"""
Multi-Agent Resume Intelligence System (MARIS)
Agent modules for collaborative resume analysis.
"""

from .base_agent import BaseAgent, AgentMessage
from .resume_parser_agent import ResumeParserAgent
from .job_analyzer_agent import JobAnalyzerAgent
from .match_scoring_agent import MatchScoringAgent
from .skill_gap_agent import SkillGapAgent
from .verification_agent import VerificationAgent

__all__ = [
    'BaseAgent',
    'AgentMessage',
    'ResumeParserAgent',
    'JobAnalyzerAgent',
    'MatchScoringAgent',
    'SkillGapAgent',
    'VerificationAgent'
]
