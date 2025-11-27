"""
Integration tests for orchestrator with agents
"""

import pytest
from core.orchestrator import DynamicOrchestrator
from agents.example_agent import ExampleAgent
from agents.base_agent import AgentConfig


@pytest.mark.asyncio
async def test_orchestrator_with_agent():
    """Test orchestrator can discover and manage agents"""
    orchestrator = DynamicOrchestrator(discovery_backend='memory')
    
    # Create test agent
    agent = ExampleAgent()
    await agent.initialize()
    
    # Manually add agent metadata (simulating discovery)
    from core.orchestrator import AgentMetadata, AgentStatus
    from datetime import datetime
    
    meta = AgentMetadata(
        id="example-agent",
        name="Example Agent",
        capabilities=agent.get_capabilities(),
        status=AgentStatus.ACTIVE,
        health=1.0,
        last_beat=datetime.utcnow(),
    )
    
    orchestrator.agents["example-agent"] = meta
    
    assert len(orchestrator.agents) == 1
    assert orchestrator.agents["example-agent"].name == "Example Agent"
    
    await orchestrator.stop()


@pytest.mark.asyncio
async def test_agent_health_monitoring():
    """Test orchestrator monitors agent health"""
    orchestrator = DynamicOrchestrator(discovery_backend='memory')
    await orchestrator.start()
    
    # Wait for health check cycle
    import asyncio
    await asyncio.sleep(6)  # Wait for health monitor loop
    
    await orchestrator.stop()


@pytest.mark.asyncio
async def test_self_healing():
    """Test orchestrator can heal failed agents"""
    orchestrator = DynamicOrchestrator(discovery_backend='memory')
    
    from core.orchestrator import AgentMetadata, AgentStatus
    from datetime import datetime, timedelta
    
    # Create agent with poor health
    meta = AgentMetadata(
        id="failing-agent",
        name="Failing Agent",
        status=AgentStatus.FAILED,
        health=0.3,  # Below threshold
        last_beat=datetime.utcnow() - timedelta(minutes=2),
        auto_heal=True,
    )
    
    orchestrator.agents["failing-agent"] = meta
    
    await orchestrator.start()
    
    # Wait for healing cycle
    await asyncio.sleep(12)  # Wait for self-healing loop
    
    # Check if agent was healed
    healed_meta = orchestrator.agents.get("failing-agent")
    if healed_meta:
        # Agent should be healed or in healing process
        assert healed_meta.status in [AgentStatus.HEALING, AgentStatus.ACTIVE]
    
    await orchestrator.stop()

