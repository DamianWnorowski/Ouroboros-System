"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def orchestrator():
    """Create orchestrator instance for testing"""
    from core.orchestrator import DynamicOrchestrator
    orch = DynamicOrchestrator(discovery_backend='memory')
    yield orch
    await orch.stop()

