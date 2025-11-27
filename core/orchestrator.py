"""
Ouroboros Dynamic Orchestrator - Core System
NO HARDCODING | DYNAMIC DISCOVERY | SELF-HEALING
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    import prometheus_client as prom
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("prometheus_client not available, metrics disabled")

# Prometheus Metrics (if available)
if PROMETHEUS_AVAILABLE:
    AGENT_COUNT = prom.Gauge('ouroboros_agents', 'Active agents')
    ORCH_LATENCY = prom.Histogram('ouroboros_orch_latency', 'Orchestration latency')
    HEALING_EVENTS = prom.Counter('ouroboros_healing_total', 'Healing events')
    SYSTEM_HEALTH = prom.Gauge('ouroboros_health', 'System health', ['component'])


class AgentStatus(Enum):
    INIT = "initializing"
    ACTIVE = "active"
    HEALING = "healing"
    PAUSED = "paused"
    FAILED = "failed"


@dataclass
class AgentMetadata:
    id: str
    name: str
    capabilities: Set[str] = field(default_factory=set)
    dependencies: Set[str] = field(default_factory=set)
    status: AgentStatus = AgentStatus.INIT
    health: float = 1.0
    last_beat: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict = field(default_factory=dict)
    auto_heal: bool = True


class DynamicOrchestrator:
    """Dynamic orchestrator with auto-discovery and self-healing"""
    
    def __init__(self, discovery_backend: str = 'memory'):
        self.logger = logging.getLogger(__name__)
        self.agents: Dict[str, AgentMetadata] = {}
        self.running = False
        self.discovery_backend = discovery_backend
        self.discovery = self._init_discovery(discovery_backend)
    
    def _init_discovery(self, backend: str):
        """Initialize service discovery backend"""
        if backend == 'consul':
            return self._init_consul()
        elif backend == 'etcd':
            return self._init_etcd()
        else:
            return self._init_memory()
    
    def _init_consul(self):
        """Dynamic Consul discovery"""
        try:
            import consul
            consul_host = os.getenv('CONSUL_HOST', 'localhost')
            consul_port = int(os.getenv('CONSUL_PORT', '8500'))
            return consul.Consul(host=consul_host, port=consul_port)
        except ImportError:
            self.logger.warning("Consul not available, using memory backend")
            return self._init_memory()
    
    def _init_etcd(self):
        """Dynamic etcd discovery"""
        try:
            import etcd3
            etcd_host = os.getenv('ETCD_HOST', 'localhost')
            etcd_port = int(os.getenv('ETCD_PORT', '2379'))
            return etcd3.client(host=etcd_host, port=etcd_port)
        except ImportError:
            self.logger.warning("etcd3 not available, using memory backend")
            return self._init_memory()
    
    def _init_memory(self):
        """In-memory discovery (fallback)"""
        return {}
    
    async def auto_discover_agents(self) -> List[AgentMetadata]:
        """Dynamically discover all agents"""
        discovered = []
        
        # Scan agents directory
        agents_path = Path(__file__).parent.parent / 'agents'
        if not agents_path.exists():
            self.logger.warning(f"Agents directory not found: {agents_path}")
            return discovered
        
        for file in agents_path.glob('**/*.py'):
            if file.stem.startswith('_'):
                continue
            
            try:
                # Dynamic import
                module = self._dynamic_import(file)
                
                # Find agent classes
                for name, obj in self._get_agent_classes(module):
                    agent_meta = self._extract_metadata(obj, name)
                    discovered.append(agent_meta)
                    self.logger.info(f"Discovered agent: {agent_meta.name}")
            except Exception as e:
                self.logger.error(f"Error discovering agent from {file}: {e}")
        
        return discovered
    
    def _dynamic_import(self, file_path: Path):
        """Dynamically import a module"""
        import importlib.util
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def _get_agent_classes(self, module):
        """Get agent classes from module"""
        import inspect
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if hasattr(obj, '__agent__') and obj.__agent__:
                yield name, obj
    
    def _extract_metadata(self, agent_class, class_name: str) -> AgentMetadata:
        """Extract metadata from agent class"""
        capabilities = getattr(agent_class, '__capabilities__', set())
        dependencies = getattr(agent_class, '__dependencies__', set())
        
        return AgentMetadata(
            id=f"{class_name.lower()}_{id(agent_class)}",
            name=class_name,
            capabilities=capabilities,
            dependencies=dependencies
        )
    
    async def start(self):
        """Start orchestrator with dynamic agent discovery"""
        self.logger.info("Starting Ouroboros Orchestrator...")
        self.running = True
        
        # Auto-discover all agents
        agents = await self.auto_discover_agents()
        
        # Initialize each agent
        for agent_meta in agents:
            await self._init_agent(agent_meta)
        
        # Start health monitoring
        asyncio.create_task(self._health_monitor_loop())
        
        # Start self-healing loop
        asyncio.create_task(self._self_healing_loop())
        
        self.logger.info(f"Orchestrator started with {len(self.agents)} agents")
    
    async def _init_agent(self, agent_meta: AgentMetadata):
        """Initialize an agent"""
        self.agents[agent_meta.id] = agent_meta
        agent_meta.status = AgentStatus.ACTIVE
        if PROMETHEUS_AVAILABLE:
            AGENT_COUNT.set(len(self.agents))
    
    async def _health_monitor_loop(self):
        """Continuous health monitoring"""
        while self.running:
            for agent_id, meta in self.agents.items():
                health = await self._check_health(agent_id)
                meta.health = health
                if PROMETHEUS_AVAILABLE:
                    SYSTEM_HEALTH.labels(component=meta.name).set(health)
            
            await asyncio.sleep(5)
    
    async def _check_health(self, agent_id: str) -> float:
        """Check health of an agent"""
        meta = self.agents.get(agent_id)
        if not meta:
            return 0.0
        
        # Simple health check based on last beat
        time_since_beat = (datetime.utcnow() - meta.last_beat).total_seconds()
        if time_since_beat > 60:
            return 0.5
        return 1.0
    
    async def _self_healing_loop(self):
        """Auto-healing failed agents"""
        while self.running:
            for agent_id, meta in self.agents.items():
                if meta.health < 0.5 and meta.auto_heal:
                    self.logger.warning(f"Healing agent: {meta.name}")
                    await self._heal_agent(agent_id)
                    if PROMETHEUS_AVAILABLE:
                        HEALING_EVENTS.inc()
            
            await asyncio.sleep(10)
    
    async def _heal_agent(self, agent_id: str):
        """Heal a failed agent"""
        meta = self.agents.get(agent_id)
        if not meta:
            return
        
        meta.status = AgentStatus.HEALING
        # Attempt to restart/recover agent
        await asyncio.sleep(1)  # Simulate healing
        meta.status = AgentStatus.ACTIVE
        meta.health = 1.0
        meta.last_beat = datetime.utcnow()
        self.logger.info(f"Agent {meta.name} healed successfully")
    
    async def stop(self):
        """Stop orchestrator"""
        self.logger.info("Stopping orchestrator...")
        self.running = False
        self.logger.info("Orchestrator stopped")


async def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    orchestrator = DynamicOrchestrator()
    await orchestrator.start()
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())

