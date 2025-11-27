"""
Example Agent Implementation
Demonstrates how to create a custom agent
"""

from typing import Dict, Any
from .base_agent import BaseAgent, AgentConfig


class ExampleAgent(BaseAgent):
    """
    Example Agent - Template for creating new agents
    
    This agent demonstrates:
    - Agent initialization
    - Task execution
    - Health checking
    - Capability definition
    """
    
    __agent__ = True
    __capabilities__ = {'example', 'demo', 'template'}
    __dependencies__ = set()
    
    def __init__(self, config: AgentConfig = None):
        if config is None:
            config = AgentConfig(
                name="Example Agent",
                capabilities=self.__capabilities__,
            )
        super().__init__(config)
        self.task_count = 0
    
    async def initialize(self):
        """Initialize the agent"""
        self.status = "active"
        self.logger.info("Example Agent initialized")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task"""
        self.task_count += 1
        self.logger.info(f"Executing task #{self.task_count}: {task}")
        
        # Simulate work
        result = {
            "agent": self.config.name,
            "task_id": task.get("id", "unknown"),
            "status": "completed",
            "task_count": self.task_count,
        }
        
        await self.heartbeat()
        return result
    
    async def health_check(self) -> float:
        """Check agent health (0.0 to 1.0)"""
        # Simple health check
        if self.status != "active":
            return 0.0
        
        # Health decreases if too many tasks without heartbeat
        if self.task_count > 1000:
            return 0.5
        
        return 1.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "name": self.config.name,
            "status": self.status,
            "task_count": self.task_count,
            "health": self.health,
        }

