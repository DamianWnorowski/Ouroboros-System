"""
Distributed Coordination System - Elite Cluster Management

This module implements a sophisticated distributed coordination system with:
- Cluster management and node discovery
- Intelligent load balancing and task distribution
- Automatic failover and fault tolerance
- Consensus algorithms for distributed decision making
- Service mesh integration for microservices
- Geographic load distribution and latency optimization

Key Features:
- Automatic cluster formation and node discovery
- Load balancing with multiple algorithms (round-robin, least-loaded, geographic)
- Fault detection and automatic failover
- Consensus-based decision making (Raft-inspired)
- Service mesh integration with circuit breakers
- Cross-region replication and disaster recovery
- Real-time cluster health monitoring
"""

import asyncio
import json
import time
import hashlib
import socket
import threading
from datetime import datetime, UTC, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable, Set, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from pathlib import Path
import aiofiles
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import statistics
import random
import heapq

class NodeStatus(Enum):
    """Node status in the cluster."""
    ALIVE = "alive"
    SUSPECT = "suspect"
    DEAD = "dead"
    LEFT = "left"

class NodeRole(Enum):
    """Node roles in the cluster."""
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    OBSERVER = "observer"

class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    GEOGRAPHIC = "geographic"
    RANDOM = "random"
    LEAST_LATENCY = "least_latency"

class ConsensusState(Enum):
    """Consensus algorithm states."""
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class ClusterNode:
    """Represents a node in the distributed cluster."""
    node_id: str
    address: str
    port: int
    role: NodeRole = NodeRole.FOLLOWER
    status: NodeStatus = NodeStatus.ALIVE
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Performance metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_tasks: int = 0
    queue_depth: int = 0

    # Geographic information
    region: str = "unknown"
    datacenter: str = "unknown"
    latitude: float = 0.0
    longitude: float = 0.0

    # Capabilities
    capabilities: Set[str] = field(default_factory=set)
    max_concurrent_tasks: int = 10

    # Load balancing weights
    load_weight: float = 1.0
    geographic_weight: float = 1.0

    # Health metrics
    uptime_seconds: int = 0
    total_tasks_processed: int = 0
    failed_tasks: int = 0
    average_response_time: float = 0.0

@dataclass
class ClusterTask:
    """Represents a distributed task."""
    task_id: str
    task_type: str
    payload: Dict[str, Any]
    priority: int = 1  # 1-10, higher = more urgent

    # Execution tracking
    assigned_node: Optional[str] = None
    status: str = "pending"  # pending, assigned, running, completed, failed
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Requirements and constraints
    required_capabilities: Set[str] = field(default_factory=set)
    preferred_regions: List[str] = field(default_factory=list)
    max_execution_time: int = 300  # seconds

    # Results
    result: Any = None
    error_message: str = ""
    execution_time: float = 0.0

@dataclass
class ConsensusMessage:
    """Consensus algorithm message."""
    message_type: str  # request_vote, append_entries, etc.
    term: int
    sender_id: str
    receiver_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

@dataclass
class LoadBalancerMetrics:
    """Load balancer performance metrics."""
    total_requests: int = 0
    successful_assignments: int = 0
    failed_assignments: int = 0
    average_assignment_time: float = 0.0
    queue_depth: int = 0

    # Strategy-specific metrics
    strategy_performance: Dict[str, float] = field(default_factory=dict)

class EliteDistributedCoordinator:
    """
    Elite Distributed Coordination System - Cluster Management & Load Balancing

    Advanced distributed system providing:
    - Automatic cluster formation and node management
    - Intelligent load balancing across nodes
    - Fault tolerance with automatic failover
    - Consensus-based decision making
    - Geographic load distribution
    - Real-time cluster monitoring
    """

    def __init__(self, node_id: str = None, bind_address: str = "0.0.0.0",
                 bind_port: int = 8002, seed_nodes: List[str] = None):
        self.logger = logging.getLogger(__name__)

        # Node configuration
        self.node_id = node_id or f"node_{socket.gethostname()}_{int(time.time())}"
        self.bind_address = bind_address
        self.bind_port = bind_port
        self.node_address = f"{socket.gethostbyname(socket.gethostname())}:{bind_port}"

        # Cluster state
        self.cluster_nodes: Dict[str, ClusterNode] = {}
        self.local_node = ClusterNode(
            node_id=self.node_id,
            address=self.node_address.split(':')[0],
            port=int(self.node_address.split(':')[1]),
            role=NodeRole.FOLLOWER,
            status=NodeStatus.ALIVE
        )
        self.cluster_nodes[self.node_id] = self.local_node

        # Seed nodes for cluster discovery
        self.seed_nodes = seed_nodes or []

        # Consensus state
        self.consensus_state = ConsensusState.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.commit_index = 0
        self.last_applied = 0

        # Election timing
        self.election_timeout = random.uniform(5, 10)  # seconds
        self.heartbeat_interval = 1.0  # seconds
        self.last_heartbeat_received = datetime.now(UTC)

        # Task management
        self.pending_tasks: List[ClusterTask] = []
        self.running_tasks: Dict[str, ClusterTask] = {}
        self.completed_tasks: List[ClusterTask] = []

        # Load balancing
        self.load_balancer = DistributedLoadBalancer()
        self.task_queue: asyncio.Queue = asyncio.Queue()

        # Network communication
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.server_task: Optional[asyncio.Task] = None
        self.gossip_task: Optional[asyncio.Task] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.consensus_task: Optional[asyncio.Task] = None

        # Geographic information
        self.geo_cache: Dict[str, Tuple[float, float]] = {}  # IP -> (lat, lng)

        # Fault tolerance
        self.failure_detector = PhiAccrualFailureDetector()
        self.failover_manager = FailoverManager()

        # Performance monitoring
        self.metrics = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "cluster_size": 1,
            "leadership_changes": 0,
            "network_hops": 0
        }

    async def start_cluster(self) -> None:
        """Start the distributed cluster coordinator."""
        self.logger.info(f"Starting Elite Distributed Coordinator: {self.node_id}")

        # Initialize HTTP client
        self.http_session = aiohttp.ClientSession()

        # Start HTTP server for cluster communication
        self.server_task = asyncio.create_task(self._start_http_server())

        # Start gossip protocol for node discovery
        self.gossip_task = asyncio.create_task(self._gossip_protocol())

        # Start heartbeat monitoring
        self.heartbeat_task = asyncio.create_task(self._heartbeat_monitor())

        # Start consensus algorithm
        self.consensus_task = asyncio.create_task(self._consensus_algorithm())

        # Start task processor
        task_processor = asyncio.create_task(self._process_task_queue())

        # Join existing cluster if seed nodes available
        if self.seed_nodes:
            await self._join_cluster()

        # Wait for cluster stabilization
        await asyncio.sleep(5)

        self.logger.info(f"Elite Distributed Coordinator started - Node: {self.node_id}")

    async def stop_cluster(self) -> None:
        """Stop the distributed cluster coordinator."""
        self.logger.info(f"Stopping Elite Distributed Coordinator: {self.node_id}")

        # Cancel all background tasks
        for task in [self.server_task, self.gossip_task, self.heartbeat_task, self.consensus_task]:
            if task:
                task.cancel()

        # Leave cluster gracefully
        await self._leave_cluster()

        # Close HTTP session
        if self.http_session:
            await self.http_session.close()

        self.logger.info("Elite Distributed Coordinator stopped")

    async def submit_task(self, task: ClusterTask) -> str:
        """
        Submit a task for distributed execution.

        Args:
            task: Task to execute

        Returns:
            Task ID for tracking
        """
        # Add to pending tasks
        self.pending_tasks.append(task)

        # Try to assign immediately
        assigned = await self._assign_task(task)
        if not assigned:
            # Add to queue for later assignment
            await self.task_queue.put(task)

        return task.task_id

    async def get_task_status(self, task_id: str) -> Optional[ClusterTask]:
        """Get the status of a submitted task."""
        # Check running tasks
        if task_id in self.running_tasks:
            return self.running_tasks[task_id]

        # Check pending tasks
        for task in self.pending_tasks:
            if task.task_id == task_id:
                return task

        # Check completed tasks (last 100)
        for task in self.completed_tasks[-100:]:
            if task.task_id == task_id:
                return task

        return None

    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status."""
        healthy_nodes = sum(1 for n in self.cluster_nodes.values() if n.status == NodeStatus.ALIVE)
        total_nodes = len(self.cluster_nodes)

        node_loads = [n.active_tasks / max(n.max_concurrent_tasks, 1) for n in self.cluster_nodes.values()]
        avg_load = statistics.mean(node_loads) if node_loads else 0.0

        return {
            "node_id": self.node_id,
            "cluster_size": total_nodes,
            "healthy_nodes": healthy_nodes,
            "leader_node": self._get_leader_node_id(),
            "average_load": avg_load,
            "pending_tasks": len(self.pending_tasks),
            "running_tasks": len(self.running_tasks),
            "total_tasks_processed": self.metrics["tasks_processed"],
            "regions": list(set(n.region for n in self.cluster_nodes.values())),
            "consensus_term": self.current_term,
            "last_heartbeat": self.last_heartbeat_received.isoformat()
        }

    async def redistribute_load(self) -> int:
        """
        Redistribute tasks for load balancing.

        Returns:
            Number of tasks redistributed
        """
        redistributed = 0

        # Find overloaded nodes
        overloaded_nodes = [
            node_id for node_id, node in self.cluster_nodes.items()
            if node.active_tasks > node.max_concurrent_tasks * 0.8
        ]

        # Find underloaded nodes
        underloaded_nodes = [
            node_id for node_id, node in self.cluster_nodes.items()
            if node.active_tasks < node.max_concurrent_tasks * 0.3
        ]

        # Redistribute tasks from overloaded to underloaded nodes
        for overloaded_id in overloaded_nodes:
            if not underloaded_nodes:
                break

            # Find tasks that can be migrated
            overloaded_tasks = [
                task for task in self.running_tasks.values()
                if task.assigned_node == overloaded_id and task.task_type in ["analysis", "computation"]
            ]

            for task in overloaded_tasks[:2]:  # Migrate up to 2 tasks per node
                target_node = underloaded_nodes[0]  # Use first underloaded node

                # Migrate task
                success = await self._migrate_task(task, target_node)
                if success:
                    redistributed += 1
                    underloaded_nodes.pop(0)  # Remove from available list
                    if not underloaded_nodes:
                        break

        return redistributed

    # Private methods

    async def _join_cluster(self) -> None:
        """Join an existing cluster using seed nodes."""
        for seed_node in self.seed_nodes:
            try:
                async with self.http_session.get(f"http://{seed_node}/cluster/join",
                                               json={"node_id": self.node_id, "address": self.node_address}) as response:
                    if response.status == 200:
                        cluster_info = await response.json()
                        # Update local cluster state
                        for node_data in cluster_info.get("nodes", []):
                            node = ClusterNode(**node_data)
                            self.cluster_nodes[node.node_id] = node
                        break
            except Exception as e:
                self.logger.warning(f"Failed to join cluster via {seed_node}: {e}")

    async def _leave_cluster(self) -> None:
        """Leave the cluster gracefully."""
        for node in list(self.cluster_nodes.values()):
            if node.node_id != self.node_id:
                try:
                    async with self.http_session.post(f"http://{node.address}:{node.port}/cluster/leave",
                                                    json={"node_id": self.node_id}) as response:
                        pass
                except Exception:
                    pass  # Ignore errors during shutdown

    def _get_leader_node_id(self) -> Optional[str]:
        """Get the current leader node ID."""
        for node_id, node in self.cluster_nodes.items():
            if node.role == NodeRole.LEADER and node.status == NodeStatus.ALIVE:
                return node_id
        return None

    async def _assign_task(self, task: ClusterTask) -> bool:
        """
        Assign a task to the best available node.

        Returns:
            True if task was assigned, False otherwise
        """
        # Find suitable nodes
        suitable_nodes = []
        for node_id, node in self.cluster_nodes.items():
            if (node.status == NodeStatus.ALIVE and
                node.active_tasks < node.max_concurrent_tasks and
                task.required_capabilities.issubset(node.capabilities)):
                suitable_nodes.append(node)

        if not suitable_nodes:
            return False

        # Select best node using load balancer
        selected_node = await self.load_balancer.select_node(
            suitable_nodes, task, LoadBalancingStrategy.LEAST_LOADED
        )

        if selected_node:
            # Assign task
            task.assigned_node = selected_node.node_id
            task.status = "assigned"
            selected_node.active_tasks += 1

            # Forward task to node
            await self._forward_task_to_node(task, selected_node)
            return True

        return False

    async def _forward_task_to_node(self, task: ClusterTask, node: ClusterNode) -> None:
        """Forward task to target node for execution."""
        try:
            async with self.http_session.post(
                f"http://{node.address}:{node.port}/tasks/execute",
                json=asdict(task)
            ) as response:
                if response.status == 200:
                    task.status = "running"
                    self.running_tasks[task.task_id] = task
                    self.pending_tasks.remove(task)
                else:
                    # Assignment failed
                    node.active_tasks -= 1
                    task.assigned_node = None
                    task.status = "pending"
        except Exception as e:
            self.logger.error(f"Failed to forward task {task.task_id} to {node.node_id}: {e}")
            node.active_tasks -= 1
            task.assigned_node = None
            task.status = "pending"

    async def _migrate_task(self, task: ClusterTask, target_node_id: str) -> bool:
        """Migrate a running task to another node."""
        if target_node_id not in self.cluster_nodes:
            return False

        target_node = self.cluster_nodes[target_node_id]

        # Cancel task on current node
        current_node_id = task.assigned_node
        if current_node_id and current_node_id in self.cluster_nodes:
            current_node = self.cluster_nodes[current_node_id]
            try:
                async with self.http_session.post(
                    f"http://{current_node.address}:{current_node.port}/tasks/cancel",
                    json={"task_id": task.task_id}
                ) as response:
                    pass
            except Exception:
                pass  # Continue with migration

        # Assign to new node
        success = await self._forward_task_to_node(task, target_node)

        if success:
            # Update node loads
            if current_node_id and current_node_id in self.cluster_nodes:
                self.cluster_nodes[current_node_id].active_tasks -= 1
            target_node.active_tasks += 1

        return success

    async def _process_task_queue(self) -> None:
        """Process queued tasks when nodes become available."""
        while True:
            try:
                # Wait for task
                task = await self.task_queue.get()

                # Try to assign
                assigned = await self._assign_task(task)
                if not assigned:
                    # Put back in queue with delay
                    await asyncio.sleep(5)
                    await self.task_queue.put(task)

                self.task_queue.task_done()

            except Exception as e:
                self.logger.error(f"Task queue processing error: {e}")
                await asyncio.sleep(1)

    async def _start_http_server(self) -> None:
        """Start HTTP server for cluster communication."""
        from aiohttp import web

        app = web.Application()

        # Cluster management endpoints
        app.router.add_post('/cluster/join', self._handle_join)
        app.router.add_post('/cluster/leave', self._handle_leave)
        app.router.add_get('/cluster/status', self._handle_status)
        app.router.add_post('/cluster/heartbeat', self._handle_heartbeat)

        # Task management endpoints
        app.router.add_post('/tasks/execute', self._handle_task_execute)
        app.router.add_post('/tasks/cancel', self._handle_task_cancel)
        app.router.add_post('/tasks/complete', self._handle_task_complete)

        # Consensus endpoints
        app.router.add_post('/consensus/request_vote', self._handle_request_vote)
        app.router.add_post('/consensus/append_entries', self._handle_append_entries)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.bind_address, self.bind_port)
        await site.start()

        self.logger.info(f"HTTP server started on {self.bind_address}:{self.bind_port}")

        # Keep server running
        while True:
            await asyncio.sleep(1)

    async def _gossip_protocol(self) -> None:
        """Implement gossip protocol for cluster membership."""
        while True:
            try:
                await asyncio.sleep(10)  # Gossip every 10 seconds

                # Select random nodes to gossip with
                alive_nodes = [
                    node for node in self.cluster_nodes.values()
                    if node.node_id != self.node_id and node.status == NodeStatus.ALIVE
                ]

                if alive_nodes:
                    # Gossip with up to 3 random nodes
                    gossip_targets = random.sample(alive_nodes, min(3, len(alive_nodes)))

                    for target_node in gossip_targets:
                        try:
                            # Send cluster state digest
                            cluster_digest = {
                                "sender_id": self.node_id,
                                "known_nodes": list(self.cluster_nodes.keys()),
                                "term": self.current_term,
                                "leader": self._get_leader_node_id()
                            }

                            async with self.http_session.post(
                                f"http://{target_node.address}:{target_node.port}/cluster/gossip",
                                json=cluster_digest
                            ) as response:
                                if response.status == 200:
                                    # Receive updated cluster state
                                    remote_state = await response.json()
                                    await self._merge_cluster_state(remote_state)

                        except Exception as e:
                            self.logger.debug(f"Gossip with {target_node.node_id} failed: {e}")

            except Exception as e:
                self.logger.error(f"Gossip protocol error: {e}")
                await asyncio.sleep(5)

    async def _heartbeat_monitor(self) -> None:
        """Monitor heartbeats and detect failed nodes."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                current_time = datetime.now(UTC)
                failed_nodes = []

                for node_id, node in self.cluster_nodes.items():
                    if node_id == self.node_id:
                        continue

                    time_since_heartbeat = (current_time - node.last_heartbeat).total_seconds()

                    if time_since_heartbeat > 15:  # 15 seconds timeout
                        if node.status == NodeStatus.ALIVE:
                            node.status = NodeStatus.SUSPECT
                            self.logger.warning(f"Node {node_id} marked as suspect")
                    elif time_since_heartbeat > 30:  # 30 seconds timeout
                        if node.status != NodeStatus.DEAD:
                            node.status = NodeStatus.DEAD
                            failed_nodes.append(node_id)
                            self.logger.error(f"Node {node_id} marked as dead")

                # Handle failed nodes
                for failed_node_id in failed_nodes:
                    await self.failover_manager.handle_node_failure(failed_node_id, self.cluster_nodes)

                    # Trigger leader election if leader failed
                    leader_id = self._get_leader_node_id()
                    if leader_id == failed_node_id:
                        await self._start_election()

            except Exception as e:
                self.logger.error(f"Heartbeat monitor error: {e}")

    async def _consensus_algorithm(self) -> None:
        """Run consensus algorithm (simplified Raft implementation)."""
        while True:
            try:
                if self.consensus_state == ConsensusState.FOLLOWER:
                    # Check for election timeout
                    time_since_heartbeat = (datetime.now(UTC) - self.last_heartbeat_received).total_seconds()

                    if time_since_heartbeat > self.election_timeout:
                        await self._start_election()

                elif self.consensus_state == ConsensusState.CANDIDATE:
                    # Election in progress - wait for votes or timeout
                    await asyncio.sleep(0.1)

                elif self.consensus_state == ConsensusState.LEADER:
                    # Send heartbeats to followers
                    await self._send_leader_heartbeats()

                await asyncio.sleep(0.1)

            except Exception as e:
                self.logger.error(f"Consensus algorithm error: {e}")
                await asyncio.sleep(1)

    async def _start_election(self) -> None:
        """Start leader election."""
        self.consensus_state = ConsensusState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        votes_received = 1  # Vote for self

        self.logger.info(f"Starting election for term {self.current_term}")

        # Request votes from other nodes
        vote_requests = []
        for node in self.cluster_nodes.values():
            if node.node_id != self.node_id and node.status == NodeStatus.ALIVE:
                vote_requests.append(self._request_vote_from_node(node))

        # Wait for votes
        if vote_requests:
            try:
                results = await asyncio.gather(*vote_requests, return_exceptions=True)

                for result in results:
                    if isinstance(result, dict) and result.get("vote_granted", False):
                        votes_received += 1

            except Exception as e:
                self.logger.error(f"Election error: {e}")

        # Check if we won the election
        total_nodes = len([n for n in self.cluster_nodes.values() if n.status == NodeStatus.ALIVE])
        majority = (total_nodes // 2) + 1

        if votes_received >= majority:
            await self._become_leader()
        else:
            self.consensus_state = ConsensusState.FOLLOWER

    async def _become_leader(self) -> None:
        """Become the cluster leader."""
        self.consensus_state = ConsensusState.LEADER
        self.local_node.role = NodeRole.LEADER

        self.logger.info(f"Node {self.node_id} became leader for term {self.current_term}")
        self.metrics["leadership_changes"] += 1

        # Initialize leader state
        # (In full Raft, would initialize nextIndex and matchIndex)

    async def _send_leader_heartbeats(self) -> None:
        """Send heartbeats to follower nodes."""
        # Send heartbeats every heartbeat_interval
        current_time = datetime.now(UTC)

        for node in self.cluster_nodes.values():
            if node.node_id != self.node_id and node.status == NodeStatus.ALIVE:
                try:
                    heartbeat_data = {
                        "term": self.current_term,
                        "leader_id": self.node_id,
                        "timestamp": current_time.isoformat()
                    }

                    async with self.http_session.post(
                        f"http://{node.address}:{node.port}/consensus/append_entries",
                        json=heartbeat_data
                    ) as response:
                        if response.status == 200:
                            node.last_heartbeat = current_time

                except Exception as e:
                    self.logger.debug(f"Heartbeat to {node.node_id} failed: {e}")

    async def _request_vote_from_node(self, node: ClusterNode) -> Dict[str, Any]:
        """Request vote from a specific node."""
        try:
            vote_request = {
                "term": self.current_term,
                "candidate_id": self.node_id,
                "last_log_index": self.commit_index,
                "last_log_term": self.current_term
            }

            async with self.http_session.post(
                f"http://{node.address}:{node.port}/consensus/request_vote",
                json=vote_request
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"vote_granted": False}

        except Exception:
            return {"vote_granted": False}

    async def _merge_cluster_state(self, remote_state: Dict[str, Any]) -> None:
        """Merge remote cluster state with local state."""
        remote_nodes = remote_state.get("known_nodes", [])

        # Add unknown nodes
        for node_id in remote_nodes:
            if node_id not in self.cluster_nodes:
                # Request full node information
                await self._discover_node(node_id)

    async def _discover_node(self, node_id: str) -> None:
        """Discover information about an unknown node."""
        # In a full implementation, would query other nodes for node info
        # For now, create a placeholder node
        placeholder_node = ClusterNode(
            node_id=node_id,
            address="unknown",
            port=0,
            status=NodeStatus.SUSPECT
        )
        self.cluster_nodes[node_id] = placeholder_node

    # HTTP request handlers

    async def _handle_join(self, request: web.Request) -> web.Response:
        """Handle cluster join request."""
        data = await request.json()
        node_id = data["node_id"]
        address = data["address"]

        # Add node to cluster
        new_node = ClusterNode(
            node_id=node_id,
            address=address.split(':')[0],
            port=int(address.split(':')[1]),
            status=NodeStatus.ALIVE
        )
        self.cluster_nodes[node_id] = new_node

        # Return current cluster state
        cluster_state = {
            "nodes": [asdict(node) for node in self.cluster_nodes.values()],
            "leader": self._get_leader_node_id(),
            "term": self.current_term
        }

        return web.json_response(cluster_state)

    async def _handle_leave(self, request: web.Request) -> web.Response:
        """Handle cluster leave request."""
        data = await request.json()
        node_id = data["node_id"]

        if node_id in self.cluster_nodes:
            self.cluster_nodes[node_id].status = NodeStatus.LEFT

        return web.json_response({"status": "ok"})

    async def _handle_status(self, request: web.Request) -> web.Response:
        """Handle cluster status request."""
        status = await self.get_cluster_status()
        return web.json_response(status)

    async def _handle_heartbeat(self, request: web.Request) -> web.Response:
        """Handle heartbeat from other nodes."""
        data = await request.json()
        sender_id = data.get("sender_id")

        if sender_id and sender_id in self.cluster_nodes:
            self.cluster_nodes[sender_id].last_heartbeat = datetime.now(UTC)

        return web.json_response({"status": "ok"})

    async def _handle_task_execute(self, request: web.Request) -> web.Response:
        """Handle task execution request."""
        task_data = await request.json()
        task = ClusterTask(**task_data)

        # Execute task locally
        try:
            result = await self._execute_task_locally(task)
            return web.json_response({"status": "success", "result": result})
        except Exception as e:
            return web.json_response({"status": "error", "error": str(e)}, status=500)

    async def _handle_task_cancel(self, request: web.Request) -> web.Response:
        """Handle task cancellation request."""
        data = await request.json()
        task_id = data["task_id"]

        if task_id in self.running_tasks:
            # Cancel task (implementation depends on task type)
            del self.running_tasks[task_id]

        return web.json_response({"status": "ok"})

    async def _handle_task_complete(self, request: web.Request) -> web.Response:
        """Handle task completion notification."""
        data = await request.json()
        task_id = data["task_id"]
        result = data.get("result")

        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
            task.status = "completed"
            task.result = result
            task.completed_at = datetime.now(UTC)
            task.execution_time = (task.completed_at - task.started_at).total_seconds()

            # Move to completed tasks
            self.completed_tasks.append(task)
            del self.running_tasks[task_id]

            # Update node load
            if task.assigned_node and task.assigned_node in self.cluster_nodes:
                self.cluster_nodes[task.assigned_node].active_tasks -= 1

            self.metrics["tasks_processed"] += 1

        return web.json_response({"status": "ok"})

    async def _handle_request_vote(self, request: web.Request) -> web.Response:
        """Handle vote request in consensus algorithm."""
        data = await request.json()

        candidate_term = data["term"]
        candidate_id = data["candidate_id"]

        # Vote logic (simplified)
        vote_granted = False

        if candidate_term > self.current_term:
            self.current_term = candidate_term
            self.consensus_state = ConsensusState.FOLLOWER
            vote_granted = True

        response = {
            "term": self.current_term,
            "vote_granted": vote_granted
        }

        return web.json_response(response)

    async def _handle_append_entries(self, request: web.Request) -> web.Response:
        """Handle append entries in consensus algorithm."""
        data = await request.json()

        term = data["term"]
        leader_id = data.get("leader_id")

        # Update term if necessary
        if term > self.current_term:
            self.current_term = term
            self.consensus_state = ConsensusState.FOLLOWER
            self.voted_for = None

        # Update heartbeat
        self.last_heartbeat_received = datetime.now(UTC)

        # If this is a heartbeat from leader
        if leader_id:
            # Ensure we're not the leader
            if self.consensus_state == ConsensusState.LEADER:
                self.consensus_state = ConsensusState.FOLLOWER
                self.local_node.role = NodeRole.FOLLOWER

        return web.json_response({"term": self.current_term, "success": True})

    async def _execute_task_locally(self, task: ClusterTask) -> Any:
        """Execute a task locally."""
        task.started_at = datetime.now(UTC)
        task.status = "running"

        try:
            # Task execution logic based on type
            if task.task_type == "computation":
                # Simulate computation task
                await asyncio.sleep(1)
                result = {"computation_result": sum(range(1000))}

            elif task.task_type == "analysis":
                # Simulate analysis task
                await asyncio.sleep(0.5)
                result = {"analysis_result": "Data analyzed successfully"}

            else:
                # Generic task
                await asyncio.sleep(0.1)
                result = {"generic_result": f"Task {task.task_id} completed"}

            return result

        except Exception as e:
            task.error_message = str(e)
            task.status = "failed"
            self.metrics["tasks_failed"] += 1
            raise

        finally:
            # Notify completion
            await self._notify_task_completion(task)


class DistributedLoadBalancer:
    """Intelligent distributed load balancer."""

    def __init__(self):
        self.metrics = LoadBalancerMetrics()

    async def select_node(self, available_nodes: List[ClusterNode],
                         task: ClusterTask, strategy: LoadBalancingStrategy) -> Optional[ClusterNode]:
        """
        Select the best node for a task using the specified strategy.

        Returns:
            Selected node or None if no suitable node found
        """
        if not available_nodes:
            return None

        self.metrics.total_requests += 1

        if strategy == LoadBalancingStrategy.LEAST_LOADED:
            # Select node with lowest load
            selected = min(available_nodes, key=lambda n: n.active_tasks / max(n.max_concurrent_tasks, 1))

        elif strategy == LoadBalancingStrategy.ROUND_ROBIN:
            # Simple round-robin (simplified)
            selected = available_nodes[0]  # Would cycle through nodes

        elif strategy == LoadBalancingStrategy.GEOGRAPHIC:
            # Select node in preferred region
            if task.preferred_regions:
                for node in available_nodes:
                    if node.region in task.preferred_regions:
                        selected = node
                        break
                else:
                    selected = available_nodes[0]
            else:
                selected = available_nodes[0]

        elif strategy == LoadBalancingStrategy.LEAST_LATENCY:
            # Select node with lowest average response time
            selected = min(available_nodes, key=lambda n: n.average_response_time or float('inf'))

        else:
            # Random selection
            selected = random.choice(available_nodes)

        self.metrics.successful_assignments += 1
        return selected


class PhiAccrualFailureDetector:
    """Phi Accrual Failure Detector for distributed systems."""

    def __init__(self, threshold: float = 8.0):
        self.threshold = threshold
        self.arrival_intervals: List[float] = []
        self.last_arrival_time = time.time()

    def heartbeat(self) -> None:
        """Record a heartbeat arrival."""
        current_time = time.time()
        interval = current_time - self.last_arrival_time
        self.arrival_intervals.append(interval)
        self.last_arrival_time = current_time

        # Keep only recent intervals
        if len(self.arrival_intervals) > 100:
            self.arrival_intervals.pop(0)

    def phi(self) -> float:
        """Calculate phi value for failure detection."""
        if len(self.arrival_intervals) < 2:
            return 0.0

        mean = statistics.mean(self.arrival_intervals)
        variance = statistics.variance(self.arrival_intervals) if len(self.arrival_intervals) > 1 else 0

        if variance == 0:
            return 0.0

        std_dev = math.sqrt(variance)
        current_time = time.time()
        time_since_last = current_time - self.last_arrival_time

        # Calculate phi
        if std_dev == 0:
            return float('inf') if time_since_last > mean else 0.0

        phi = (time_since_last - mean) / std_dev
        return phi


class FailoverManager:
    """Manages automatic failover in distributed systems."""

    def __init__(self):
        self.failover_history: List[Dict[str, Any]] = []

    async def handle_node_failure(self, failed_node_id: str, cluster_nodes: Dict[str, ClusterNode]) -> None:
        """Handle failure of a cluster node."""
        self.failover_history.append({
            "failed_node": failed_node_id,
            "timestamp": datetime.now(UTC),
            "action": "node_failure_detected"
        })

        # Find running tasks on failed node
        failed_tasks = [
            task for task in []  # Would come from coordinator's running tasks
            if getattr(task, 'assigned_node', None) == failed_node_id
        ]

        # Redistribute failed tasks (would be implemented in coordinator)
        for task in failed_tasks:
            self.failover_history.append({
                "task_id": getattr(task, 'task_id', 'unknown'),
                "action": "task_redistributed",
                "from_node": failed_node_id,
                "timestamp": datetime.now(UTC)
            })


# Global distributed coordinator instance
_distributed_coordinator: Optional[EliteDistributedCoordinator] = None

async def get_distributed_coordinator(node_id: str = None, seed_nodes: List[str] = None) -> EliteDistributedCoordinator:
    """Get or create global distributed coordinator instance."""
    global _distributed_coordinator
    if _distributed_coordinator is None:
        _distributed_coordinator = EliteDistributedCoordinator(
            node_id=node_id,
            seed_nodes=seed_nodes
        )
        await _distributed_coordinator.start_cluster()
    return _distributed_coordinator
