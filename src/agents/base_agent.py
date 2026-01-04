"""
Base Agent Class for Multi-Agent Resume Intelligence System (MARIS)
Defines the communication protocol and base structure for all agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class AgentMessage:
    """Structured message format for agent communication."""
    agent: str
    output: Dict[str, Any]
    confidence: float
    reasoning: Optional[str] = None
    evidence: Optional[List[str]] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class BaseAgent(ABC):
    """Base class for all agents in the MARIS system."""
    
    def __init__(self, agent_name: str):
        """
        Initialize agent.
        
        Args:
            agent_name: Unique identifier for this agent
        """
        self.agent_name = agent_name
        self.confidence_threshold = 0.7
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> AgentMessage:
        """
        Process input and return structured message.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            AgentMessage with results
        """
        pass
    
    def validate_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate agent output before sending.
        
        Args:
            output: Output dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        return isinstance(output, dict) and len(output) > 0
    
    def calculate_confidence(self, output: Dict[str, Any]) -> float:
        """
        Calculate confidence score for output.
        
        Args:
            output: Output dictionary
            
        Returns:
            Confidence score between 0 and 1
        """
        # Base implementation: simple heuristic
        if not output:
            return 0.0
        
        # More keys = higher confidence (simple heuristic)
        key_count = len(output)
        confidence = min(1.0, key_count / 10.0)
        
        return round(confidence, 2)
    
    def create_message(
        self,
        output: Dict[str, Any],
        confidence: Optional[float] = None,
        reasoning: Optional[str] = None,
        evidence: Optional[List[str]] = None
    ) -> AgentMessage:
        """
        Create structured agent message.
        
        Args:
            output: Agent output dictionary
            confidence: Confidence score (auto-calculated if None)
            reasoning: Reasoning summary
            evidence: List of evidence used
            
        Returns:
            AgentMessage instance
        """
        if confidence is None:
            confidence = self.calculate_confidence(output)
        
        return AgentMessage(
            agent=self.agent_name,
            output=output,
            confidence=confidence,
            reasoning=reasoning,
            evidence=evidence
        )
