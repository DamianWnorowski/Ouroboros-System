#!/usr/bin/env python3
"""
Load Testing Framework for Ouroboros System

Simulates real-world usage patterns:
- Multiple concurrent users
- Mixed workload patterns
- Stress testing under high load
- Bottleneck identification
- Scalability testing
"""

import asyncio
import time
import aiohttp
import statistics
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import sys
import os
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.orchestrator import DynamicOrchestrator
from agents.example_agent import ExampleAgent
from agents.base_agent import AgentConfig


class LoadTestScenario:
    """Represents a load testing scenario"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.requests: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()

    def add_request(self, response_time: float, success: bool, error_msg: str = None):
        self.requests.append({
            'timestamp': datetime.utcnow().isoformat(),
            'response_time': response_time,
            'success': success,
            'error': error_msg
        })
        if not success:
            self.errors.append({
                'timestamp': datetime.utcnow().isoformat(),
                'error': error_msg,
                'response_time': response_time
            })

    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    @property
    def total_requests(self) -> int:
        return len(self.requests)

    @property
    def successful_requests(self) -> int:
        return len([r for r in self.requests if r['success']])

    @property
    def failed_requests(self) -> int:
        return len([r for r in self.requests if not r['success']])

    @property
    def success_rate(self) -> float:
        if not self.requests:
            return 0.0
        return self.successful_requests / self.total_requests * 100

    @property
    def avg_response_time(self) -> float:
        if not self.requests:
            return 0.0
        return statistics.mean(r['response_time'] for r in self.requests)

    @property
    def median_response_time(self) -> float:
        if not self.requests:
            return 0.0
        return statistics.median(r['response_time'] for r in self.requests)

    @property
    def p95_response_time(self) -> float:
        if not self.requests:
            return 0.0
        sorted_times = sorted(r['response_time'] for r in self.requests)
        p95_index = int(len(sorted_times) * 0.95)
        return sorted_times[min(p95_index, len(sorted_times) - 1)]

    @property
    def requests_per_second(self) -> float:
        if self.duration == 0:
            return 0.0
        return self.total_requests / self.duration


class LoadTester:
    """Load testing framework"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.orchestrator = None
        self.agents = []
        self.executor = ThreadPoolExecutor(max_workers=10)

    async def setup_system(self, num_agents: int = 10):
        """Set up the system with agents for testing"""
        print(f"[SETUP] Creating orchestrator with {num_agents} agents...")

        self.orchestrator = DynamicOrchestrator(discovery_backend='memory')

        # Create multiple agents
        for i in range(num_agents):
            agent = ExampleAgent(AgentConfig(
                name=f"LoadTestAgent-{i}",
                capabilities={'load_test', f'capability-{i}'}
            ))
            self.agents.append(agent)

            # Add to orchestrator
            from core.orchestrator import AgentMetadata, AgentStatus
            meta = AgentMetadata(
                id=f"load-agent-{i}",
                name=agent.config.name,
                capabilities=agent.get_capabilities(),
                status=AgentStatus.ACTIVE,
                health=1.0,
                last_beat=datetime.utcnow(),
            )
            self.orchestrator.agents[meta.id] = meta

        print(f"[SETUP] System ready with {len(self.agents)} agents")

    async def simulate_user_request(self, user_id: int, scenario: LoadTestScenario) -> None:
        """Simulate a single user request"""
        try:
            # Randomly select an agent
            agent = self.agents[user_id % len(self.agents)]

            # Create a task
            task = {
                'id': f'load-task-{user_id}-{int(time.time()*1000)}',
                'type': 'load_test',
                'user_id': user_id,
                'data': {'payload': 'x' * 100}  # 100 char payload
            }

            start_time = time.time()
            result = await agent.execute(task)
            response_time = time.time() - start_time

            success = result.get('status') == 'completed'
            scenario.add_request(response_time, success)

        except Exception as e:
            response_time = time.time() - time.time()  # Minimal time for failed requests
            scenario.add_request(response_time, False, str(e))

    async def run_concurrent_users_scenario(self, num_users: int, duration_seconds: int) -> LoadTestScenario:
        """Run concurrent users scenario"""
        scenario = LoadTestScenario(
            "concurrent_users",
            f"{num_users} concurrent users for {duration_seconds} seconds"
        )

        print(f"[LOAD_TEST] Starting concurrent users test: {num_users} users, {duration_seconds}s duration")
        scenario.start()

        # Create tasks for all users
        tasks = []
        end_time = time.time() + duration_seconds

        while time.time() < end_time:
            # Launch batch of concurrent requests
            batch_tasks = []
            for user_id in range(num_users):
                task = self.simulate_user_request(user_id, scenario)
                batch_tasks.append(task)

            # Wait for batch to complete
            await asyncio.gather(*batch_tasks, return_exceptions=True)

        scenario.end()
        return scenario

    async def run_ramp_up_scenario(self, max_users: int, ramp_duration: int, steady_duration: int) -> LoadTestScenario:
        """Run ramp-up load scenario"""
        scenario = LoadTestScenario(
            "ramp_up",
            f"Ramp up to {max_users} users over {ramp_duration}s, then steady for {steady_duration}s"
        )

        print(f"[LOAD_TEST] Starting ramp-up test: 0-{max_users} users over {ramp_duration}s")
        scenario.start()

        total_duration = ramp_duration + steady_duration
        end_time = time.time() + total_duration

        while time.time() < end_time:
            elapsed = time.time() - scenario.start_time
            if elapsed < ramp_duration:
                # Ramp up phase
                current_users = int((elapsed / ramp_duration) * max_users) + 1
            else:
                # Steady state phase
                current_users = max_users

            # Launch concurrent requests
            batch_tasks = []
            for user_id in range(current_users):
                task = self.simulate_user_request(user_id, scenario)
                batch_tasks.append(task)

            await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Small delay between batches
            await asyncio.sleep(0.1)

        scenario.end()
        return scenario

    async def run_stress_test_scenario(self, num_users: int, duration_seconds: int) -> LoadTestScenario:
        """Run stress test with high load"""
        scenario = LoadTestScenario(
            "stress_test",
            f"Stress test with {num_users} concurrent users for {duration_seconds} seconds"
        )

        print(f"[LOAD_TEST] Starting stress test: {num_users} users, {duration_seconds}s")
        scenario.start()

        end_time = time.time() + duration_seconds
        tasks_completed = 0

        while time.time() < end_time:
            # Launch maximum concurrent load
            batch_tasks = []
            for user_id in range(num_users):
                task = self.simulate_user_request(user_id + tasks_completed, scenario)
                batch_tasks.append(task)

            await asyncio.gather(*batch_tasks, return_exceptions=True)
            tasks_completed += num_users

        scenario.end()
        return scenario

    def print_scenario_results(self, scenario: LoadTestScenario):
        """Print detailed results for a scenario"""
        print(f"\n=== {scenario.name.upper()} RESULTS ===")
        print(f"Description: {scenario.description}")
        print(f"Duration: {scenario.duration:.2f}s")
        print(f"Total Requests: {scenario.total_requests}")
        print(f"Successful: {scenario.successful_requests}")
        print(f"Failed: {scenario.failed_requests}")
        print(f"Success Rate: {scenario.success_rate:.2f}%")
        print(f"Requests/Second: {scenario.requests_per_second:.2f}")
        print(f"Avg Response Time: {scenario.avg_response_time*1000:.2f}ms")
        print(f"Median Response Time: {scenario.median_response_time*1000:.2f}ms")
        print(f"P95 Response Time: {scenario.p95_response_time*1000:.2f}ms")

        if scenario.errors:
            print(f"\nErrors ({len(scenario.errors)}):")
            for error in scenario.errors[:5]:  # Show first 5 errors
                print(f"  - {error['error']}")

    async def run_full_load_test_suite(self) -> Dict[str, Any]:
        """Run complete load testing suite"""
        print("=== OUROBOROS SYSTEM LOAD TESTING SUITE ===")
        print("==========================================")

        # Setup system
        await self.setup_system(num_agents=20)

        results = {
            'test_info': {
                'timestamp': datetime.utcnow().isoformat(),
                'num_agents': len(self.agents)
            },
            'scenarios': {}
        }

        # Run different load scenarios
        scenarios = []

        # 1. Light concurrent load
        scenario1 = await self.run_concurrent_users_scenario(num_users=5, duration_seconds=10)
        scenarios.append(('light_load', scenario1))

        # 2. Medium concurrent load
        scenario2 = await self.run_concurrent_users_scenario(num_users=20, duration_seconds=15)
        scenarios.append(('medium_load', scenario2))

        # 3. Ramp-up test
        scenario3 = await self.run_ramp_up_scenario(max_users=30, ramp_duration=20, steady_duration=10)
        scenarios.append(('ramp_up', scenario3))

        # 4. Stress test
        scenario4 = await self.run_stress_test_scenario(num_users=50, duration_seconds=20)
        scenarios.append(('stress_test', scenario4))

        # Store results
        for name, scenario in scenarios:
            results['scenarios'][name] = {
                'name': scenario.name,
                'description': scenario.description,
                'duration': scenario.duration,
                'total_requests': scenario.total_requests,
                'successful_requests': scenario.successful_requests,
                'failed_requests': scenario.failed_requests,
                'success_rate': scenario.success_rate,
                'requests_per_second': scenario.requests_per_second,
                'avg_response_time': scenario.avg_response_time,
                'median_response_time': scenario.median_response_time,
                'p95_response_time': scenario.p95_response_time,
                'errors': scenario.errors
            }
            self.print_scenario_results(scenario)

        # Cleanup
        if self.orchestrator:
            await self.orchestrator.stop()

        print("\n=== LOAD TESTING COMPLETE ===")
        return results

    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save load test results to file"""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"load_test_results_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to {filename}")
        return filename


async def main():
    """Main load testing execution"""
    tester = LoadTester()

    try:
        results = await tester.run_full_load_test_suite()

        # Save results
        filename = tester.save_results(results)
        print(f"\nDetailed results saved to: {filename}")

    except Exception as e:
        print(f"Load testing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
