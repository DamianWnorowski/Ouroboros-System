"""
Example: Creating a Custom Agent

This example shows how to create and use a custom agent with the Ouroboros System.
"""

import asyncio
from agents.example_agent import ExampleAgent
from agents.base_agent import AgentConfig


async def main():
    """Example usage of a custom agent"""
    
    # Create agent configuration
    config = AgentConfig(
        name="My Custom Agent",
        capabilities={'custom', 'example'},
        auto_heal=True,
    )
    
    # Create agent instance
    agent = ExampleAgent(config)
    
    # Initialize
    await agent.initialize()
    print(f"Agent initialized: {agent.config.name}")
    print(f"Status: {agent.status}")
    print(f"Capabilities: {agent.get_capabilities()}")
    
    # Execute a task
    task = {
        "id": "task-001",
        "type": "example",
        "data": {"message": "Hello from task"},
    }
    
    result = await agent.execute(task)
    print(f"Task result: {result}")
    
    # Check health
    health = await agent.health_check()
    print(f"Agent health: {health}")
    
    # Get statistics
    stats = agent.get_stats()
    print(f"Agent stats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())

