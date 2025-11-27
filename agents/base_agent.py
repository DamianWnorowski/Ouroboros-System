"""
Base Agent Class - All agents inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Set
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentConfig:
    """Agent configuration"""
    name: str
    capabilities: Set[str]
    dependencies: Set[str] = None
    auto_heal: bool = True
    health_check_interval: int = 30


class BaseAgent(ABC):
    """Base class for all Ouroboros agents"""
    
    __agent__ = True
    __capabilities__: Set[str] = set()
    __dependencies__: Set[str] = set()
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.status = "initializing"
        self.last_heartbeat = datetime.utcnow()
        self.metrics: Dict[str, Any] = {}
    
    @abstractmethod
    async def initialize(self):
        """Initialize the agent"""
        pass
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task"""
        pass
    
    @abstractmethod
    async def health_check(self) -> float:
        """Check agent health (0.0 to 1.0)"""
        pass
    
    async def heartbeat(self):
        """Send heartbeat"""
        self.last_heartbeat = datetime.utcnow()
    
    def get_capabilities(self) -> Set[str]:
        """Get agent capabilities"""
        return self.__capabilities__ or self.config.capabilities
    
    def get_dependencies(self) -> Set[str]:
        """Get agent dependencies"""
        return self.__dependencies__ or (self.config.dependencies or set())

