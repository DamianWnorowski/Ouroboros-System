"""
Unit tests for orchestrator
"""

import pytest
from core.orchestrator import DynamicOrchestrator, AgentStatus


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator can be initialized"""
    orch = DynamicOrchestrator(discovery_backend='memory')
    assert orch is not None
    assert not orch.running
    await orch.stop()


@pytest.mark.asyncio
async def test_orchestrator_start_stop():
    """Test orchestrator can start and stop"""
    orch = DynamicOrchestrator(discovery_backend='memory')
    await orch.start()
    assert orch.running
    await orch.stop()
    assert not orch.running


@pytest.mark.asyncio
async def test_agent_discovery():
    """Test agent discovery"""
    orch = DynamicOrchestrator(discovery_backend='memory')
    agents = await orch.auto_discover_agents()
    # Should return list (may be empty if no agents exist)
    assert isinstance(agents, list)

