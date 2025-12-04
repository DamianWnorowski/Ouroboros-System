#!/usr/bin/env python3
"""
Performance Benchmarking Script for Ouroboros System

This script establishes baseline performance metrics for:
- Orchestrator startup time
- Agent discovery and loading
- Task execution throughput
- Memory and CPU usage
- System responsiveness under load
"""

import asyncio
import time
import psutil
import os
from typing import Dict, List, Any
from datetime import datetime
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import DynamicOrchestrator
from agents.example_agent import ExampleAgent
from agents.base_agent import AgentConfig


class PerformanceBenchmark:
    """Performance benchmarking suite"""

    def __init__(self):
        self.results = {}
        self.process = psutil.Process()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB

    def measure_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024

    def measure_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return self.process.cpu_percent(interval=0.1)

    async def benchmark_orchestrator_startup(self) -> Dict[str, Any]:
        """Benchmark orchestrator startup time"""
        print("[BENCHMARK] Testing orchestrator startup...")

        start_time = time.time()
        start_memory = self.measure_memory_usage()

        orchestrator = DynamicOrchestrator(discovery_backend='memory')

        startup_time = time.time() - start_time
        memory_used = self.measure_memory_usage() - start_memory

        await orchestrator.stop()

        return {
            'startup_time_seconds': startup_time,
            'memory_used_mb': memory_used,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def benchmark_agent_discovery(self, num_agents: int = 5) -> Dict[str, Any]:
        """Benchmark agent discovery performance"""
        print(f"[BENCHMARK] Testing discovery of {num_agents} agents...")

        orchestrator = DynamicOrchestrator(discovery_backend='memory')

        # Create test agents
        agents = []
        for i in range(num_agents):
            agent = ExampleAgent(AgentConfig(
                name=f"TestAgent-{i}",
                capabilities={f'capability-{i}'}
            ))
            agents.append(agent)

        start_time = time.time()
        start_memory = self.measure_memory_usage()

        # Manually add agents (simulating discovery)
        for i, agent in enumerate(agents):
            from core.orchestrator import AgentMetadata, AgentStatus
            meta = AgentMetadata(
                id=f"test-agent-{i}",
                name=agent.config.name,
                capabilities=agent.get_capabilities(),
                status=AgentStatus.ACTIVE,
                health=1.0,
                last_beat=datetime.utcnow(),
            )
            orchestrator.agents[meta.id] = meta

        discovery_time = time.time() - start_time
        memory_used = self.measure_memory_usage() - start_memory

        await orchestrator.stop()

        return {
            'num_agents': num_agents,
            'discovery_time_seconds': discovery_time,
            'memory_used_mb': memory_used,
            'agents_per_second': num_agents / discovery_time if discovery_time > 0 else 0,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def benchmark_task_execution(self, num_tasks: int = 50) -> Dict[str, Any]:
        """Benchmark task execution throughput"""
        print(f"[BENCHMARK] Testing execution of {num_tasks} tasks...")

        orchestrator = DynamicOrchestrator(discovery_backend='memory')
        agent = ExampleAgent()

        # Add agent to orchestrator
        from core.orchestrator import AgentMetadata, AgentStatus
        meta = AgentMetadata(
            id="benchmark-agent",
            name=agent.config.name,
            capabilities=agent.get_capabilities(),
            status=AgentStatus.ACTIVE,
            health=1.0,
            last_beat=datetime.utcnow(),
        )
        orchestrator.agents[meta.id] = meta

        # Prepare tasks
        tasks = []
        for i in range(num_tasks):
            tasks.append({
                'id': f'task-{i}',
                'type': 'benchmark',
                'data': {'iteration': i}
            })

        start_time = time.time()
        start_memory = self.measure_memory_usage()

        # Execute tasks
        results = []
        for task in tasks:
            result = await agent.execute(task)
            results.append(result)

        execution_time = time.time() - start_time
        memory_used = self.measure_memory_usage() - start_memory

        await orchestrator.stop()

        return {
            'num_tasks': num_tasks,
            'total_execution_time_seconds': execution_time,
            'average_task_time_seconds': execution_time / num_tasks,
            'tasks_per_second': num_tasks / execution_time,
            'memory_used_mb': memory_used,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def benchmark_system_load(self, duration_seconds: int = 30) -> Dict[str, Any]:
        """Benchmark system under continuous load"""
        print(f"[BENCHMARK] Testing system under load for {duration_seconds} seconds...")

        orchestrator = DynamicOrchestrator(discovery_backend='memory')
        agent = ExampleAgent()

        # Add agent
        from core.orchestrator import AgentMetadata, AgentStatus
        meta = AgentMetadata(
            id="load-test-agent",
            name=agent.config.name,
            capabilities=agent.get_capabilities(),
            status=AgentStatus.ACTIVE,
            health=1.0,
            last_beat=datetime.utcnow(),
        )
        orchestrator.agents[meta.id] = meta

        start_time = time.time()
        task_count = 0
        memory_readings = []
        cpu_readings = []

        while time.time() - start_time < duration_seconds:
            # Execute task
            task = {'id': f'load-task-{task_count}', 'type': 'load_test'}
            await agent.execute(task)
            task_count += 1

            # Record system metrics every 10 tasks
            if task_count % 10 == 0:
                memory_readings.append(self.measure_memory_usage())
                cpu_readings.append(self.measure_cpu_usage())

        total_time = time.time() - start_time

        await orchestrator.stop()

        return {
            'duration_seconds': duration_seconds,
            'tasks_completed': task_count,
            'tasks_per_second': task_count / total_time,
            'average_memory_mb': sum(memory_readings) / len(memory_readings) if memory_readings else 0,
            'peak_memory_mb': max(memory_readings) if memory_readings else 0,
            'average_cpu_percent': sum(cpu_readings) / len(cpu_readings) if cpu_readings else 0,
            'peak_cpu_percent': max(cpu_readings) if cpu_readings else 0,
            'timestamp': datetime.utcnow().isoformat()
        }

    async def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark suite"""
        print("=== Starting Ouroboros System Performance Benchmark ===")
        print("=" * 50)

        results = {
            'benchmark_info': {
                'timestamp': datetime.utcnow().isoformat(),
                'python_version': sys.version,
                'platform': sys.platform,
                'cpu_count': os.cpu_count(),
                'total_memory_mb': psutil.virtual_memory().total / 1024 / 1024
            }
        }

        # Run individual benchmarks
        results['orchestrator_startup'] = await self.benchmark_orchestrator_startup()
        results['agent_discovery'] = await self.benchmark_agent_discovery()
        results['task_execution'] = await self.benchmark_task_execution()
        results['system_load'] = await self.benchmark_system_load()

        print("Benchmark complete!")
        return results

    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save benchmark results to file"""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_results_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to {filename}")
        return filename

    def print_summary(self, results: Dict[str, Any]):
        """Print benchmark summary"""
        print("\n=== PERFORMANCE BENCHMARK SUMMARY ===")
        print("=" * 50)

        startup = results.get('orchestrator_startup', {})
        discovery = results.get('agent_discovery', {})
        execution = results.get('task_execution', {})
        load = results.get('system_load', {})

        print(f"Orchestrator Startup:")
        print(f"   Startup Time: {startup.get('startup_time_seconds', 0):.2f}s")
        print(f"   Memory Used: {startup.get('memory_used_mb', 0):.1f}MB")

        print(f"Agent Discovery:")
        print(f"   Discovery Time: {discovery.get('discovery_time_seconds', 0):.3f}s")
        print(f"   Memory Used: {discovery.get('memory_used_mb', 0):.1f}MB")
        print(f"   Agents/Second: {discovery.get('agents_per_second', 0):.1f}")

        print(f"Task Execution:")
        print(f"   Total Time: {execution.get('total_execution_time_seconds', 0):.3f}s")
        print(f"   Avg Task Time: {execution.get('average_task_time_seconds', 0):.1f}ms")
        print(f"   Memory Used: {execution.get('memory_used_mb', 0):.1f}MB")
        print(f"   Tasks/Second: {execution.get('tasks_per_second', 0):.2f}")

        print(f"System Load:")
        print(f"   Tasks Completed: {load.get('tasks_completed', 0)}")
        print(f"   Tasks/Second: {load.get('tasks_per_second', 0):.1f}")
        print(f"   Avg Memory: {load.get('average_memory_mb', 0):.1f}MB")
        print(f"   Peak Memory: {load.get('peak_memory_mb', 0):.1f}MB")
        print(f"   Avg CPU: {load.get('average_cpu_percent', 0):.1f}%")
        print(f"   Peak CPU: {load.get('peak_cpu_percent', 0):.1f}%")


async def main():
    """Main benchmark execution"""
    benchmark = PerformanceBenchmark()

    try:
        results = await benchmark.run_full_benchmark()
        benchmark.print_summary(results)

        # Save results
        filename = benchmark.save_results(results)
        print(f"\nDetailed results saved to: {filename}")

    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
