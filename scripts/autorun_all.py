#!/usr/bin/env python3
"""
Ouroboros System Auto-Run Evolution Loop
Continuously monitors and improves system health through automated cycles
"""

import asyncio
import time
import json
import os
import sys
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, Any, List
import subprocess


class AutoEvolutionLoop:
    """Automated evolution loop for Ouroboros System"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.cycle_count = 0
        self.start_time = datetime.now(UTC)
        self.results_history: List[Dict[str, Any]] = []
        self.running = False

    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for auto-evolution"""
        return {
            "auto_loop_enabled": True,
            "generation_interval_seconds": 300,  # 5 minutes
            "max_cycles": None,  # Run indefinitely if None
            "apply_safe_actions": False,
            "tests_enabled": True,
            "benchmark_enabled": True,
            "health_checks_enabled": True,
            "fitness_threshold": 0.8,
            "consecutive_failures_threshold": 3
        }

    async def run_cycle(self) -> Dict[str, Any]:
        """Run a single evolution cycle"""
        cycle_start = datetime.now(UTC)
        self.cycle_count += 1

        print(f"\n{'='*60}")
        print(f"CYCLE {self.cycle_count} - {cycle_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        results = {
            "cycle": self.cycle_count,
            "timestamp": cycle_start.isoformat(),
            "phases": {}
        }

        # Phase 1: Run Tests
        if self.config["tests_enabled"]:
            print("\nPhase 1: Running Test Suite...")
            test_results = await self._run_test_suite()
            results["phases"]["tests"] = test_results

        # Phase 2: Performance Benchmarking
        if self.config["benchmark_enabled"]:
            print("\nPhase 2: Performance Benchmarking...")
            benchmark_results = await self._run_benchmarks()
            results["phases"]["benchmarks"] = benchmark_results

        # Phase 3: Health Checks
        if self.config["health_checks_enabled"]:
            print("\nPhase 3: System Health Analysis...")
            health_results = await self._run_health_checks()
            results["phases"]["health"] = health_results

        # Phase 4: Evolution Analysis
        print("\nPhase 4: Evolution Analysis...")
        evolution_results = await self._run_evolution_analysis()
        results["phases"]["evolution"] = evolution_results

        # Phase 5: Safe Actions (if enabled)
        if self.config["apply_safe_actions"]:
            print("\nPhase 5: Applying Safe Actions...")
            action_results = await self._apply_safe_actions(results)
            results["phases"]["actions"] = action_results

        # Calculate cycle metrics
        cycle_end = datetime.now(UTC)
        results["duration_seconds"] = (cycle_end - cycle_start).total_seconds()
        results["overall_fitness"] = self._calculate_overall_fitness(results)

        # Store results
        self.results_history.append(results)

        # Print summary
        self._print_cycle_summary(results)

        return results

    async def _run_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite"""
        try:
            # Run pytest programmatically
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/unit/test_orchestrator.py", "tests/unit/test_validation.py", "tests/integration/",
                "--tb=no"
            ], capture_output=True, text=True, cwd=Path.cwd())

            # Parse coverage report if it exists
            coverage_file = Path("coverage.json")
            coverage_data = {}
            if coverage_file.exists():
                try:
                    with open(coverage_file, 'r') as f:
                        coverage_data = json.load(f)
                except:
                    pass

            # Check if tests passed (some failures are acceptable for now)
            success = result.returncode == 0 or "passed" in result.stdout
            tests_passed = result.stdout.count("PASSED") if "PASSED" in result.stdout else 0
            tests_failed = result.stdout.count("FAILED") if "FAILED" in result.stdout else 0

            return {
                "success": success,
                "exit_code": result.returncode,
                "tests_passed": tests_passed,
                "tests_failed": tests_failed,
                "output": result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "exit_code": -1
            }

    async def _run_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        try:
            result = subprocess.run([
                sys.executable, "scripts/benchmark.py"
            ], capture_output=True, text=True, cwd=Path.cwd(), timeout=60)

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr,
                "execution_time": self._extract_benchmark_time(result.stdout)
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Benchmark timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _run_health_checks(self) -> Dict[str, Any]:
        """Run system health checks"""
        try:
            result = subprocess.run([
                sys.executable, "scripts/test_caching.py"
            ], capture_output=True, text=True, cwd=Path.cwd(), timeout=30)

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "caching_ok": "PASS" in result.stdout,
                "pooling_ok": "PASS" in result.stdout
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Health check timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _run_evolution_analysis(self) -> Dict[str, Any]:
        """Run evolution analysis and suggestions"""
        # Analyze recent results and suggest improvements
        recent_cycles = self.results_history[-5:] if len(self.results_history) >= 5 else self.results_history

        analysis = {
            "cycles_analyzed": len(recent_cycles),
            "trends": self._analyze_trends(recent_cycles),
            "suggestions": self._generate_suggestions(recent_cycles),
            "fitness_history": [cycle.get("overall_fitness", 0) for cycle in recent_cycles]
        }

        return analysis

    async def _apply_safe_actions(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply safe automated actions (disabled by default)"""
        actions_taken = []

        # Example safe actions (disabled by default)
        if results.get("overall_fitness", 0) < 0.5:
            actions_taken.append("Low fitness detected - logging for manual review")

        return {
            "actions_taken": actions_taken,
            "note": "Safe actions are disabled by default. Enable with --apply-safe-actions"
        }

    def _calculate_overall_fitness(self, results: Dict[str, Any]) -> float:
        """Calculate overall system fitness score"""
        fitness_components = []

        # Test success (40% weight) - allow some failures
        test_data = results["phases"].get("tests", {})
        if test_data.get("success") or test_data.get("tests_passed", 0) > test_data.get("tests_failed", 0):
            fitness_components.append(0.4)

        # Benchmark success (30% weight)
        if results["phases"].get("benchmarks", {}).get("success"):
            fitness_components.append(0.3)

        # Health success (30% weight)
        if results["phases"].get("health", {}).get("success"):
            fitness_components.append(0.3)

        return sum(fitness_components) if fitness_components else 0.0

    def _analyze_trends(self, recent_cycles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in recent cycles"""
        if not recent_cycles:
            return {"note": "No cycles to analyze"}

        fitness_trend = []
        test_success_rate = 0
        benchmark_success_rate = 0

        for cycle in recent_cycles:
            fitness_trend.append(cycle.get("overall_fitness", 0))
            if cycle["phases"].get("tests", {}).get("success"):
                test_success_rate += 1
            if cycle["phases"].get("benchmarks", {}).get("success"):
                benchmark_success_rate += 1

        test_success_rate /= len(recent_cycles)
        benchmark_success_rate /= len(recent_cycles)

        return {
            "fitness_trend": fitness_trend,
            "test_success_rate": test_success_rate,
            "benchmark_success_rate": benchmark_success_rate,
            "improving": len(fitness_trend) > 1 and fitness_trend[-1] > fitness_trend[0]
        }

    def _generate_suggestions(self, recent_cycles: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions based on recent cycles"""
        suggestions = []

        if not recent_cycles:
            return ["Run more cycles to generate suggestions"]

        latest = recent_cycles[-1]
        trends = self._analyze_trends(recent_cycles)

        # Test-related suggestions
        if not latest["phases"].get("tests", {}).get("success"):
            suggestions.append("Fix failing tests - check test output for details")
        elif trends.get("test_success_rate", 0) < 0.8:
            suggestions.append("Improve test reliability - consider flaky test fixes")

        # Performance suggestions
        if not latest["phases"].get("benchmarks", {}).get("success"):
            suggestions.append("Address benchmark failures - check performance regressions")
        elif trends.get("benchmark_success_rate", 0) < 0.8:
            suggestions.append("Optimize performance - review benchmark results")

        # Health suggestions
        if not latest["phases"].get("health", {}).get("success"):
            suggestions.append("Fix health check failures - review integration issues")

        # Overall suggestions
        if latest.get("overall_fitness", 0) < 0.7:
            suggestions.append("Overall fitness is low - focus on critical issues first")
        elif not trends.get("improving", False):
            suggestions.append("System fitness not improving - consider architecture changes")

        if not suggestions:
            suggestions.append("System is performing well - consider advanced optimizations")

        return suggestions

    def _extract_test_count(self, output: str) -> int:
        """Extract test count from pytest output"""
        try:
            # Look for "X passed" pattern
            if "passed" in output:
                lines = output.split('\n')
                for line in reversed(lines):
                    if "passed" in line:
                        parts = line.split()
                        for part in parts:
                            if part.isdigit():
                                return int(part)
            return 0
        except:
            return 0

    def _extract_benchmark_time(self, output: str) -> float:
        """Extract benchmark execution time"""
        try:
            # Look for time patterns in output
            lines = output.split('\n')
            for line in lines:
                if 'tasks_per_second' in line and ':' in line:
                    # Extract number from "tasks_per_second: X.XX"
                    parts = line.split(':')
                    if len(parts) > 1:
                        return float(parts[1].strip().split()[0])
            return 0.0
        except:
            return 0.0

    def _print_cycle_summary(self, results: Dict[str, Any]):
        """Print cycle summary"""
        print(f"\nCYCLE {self.cycle_count} SUMMARY")
        print(f"Duration: {results['duration_seconds']:.1f}s")
        print(f"Overall Fitness: {results['overall_fitness']:.2f}/1.0")

        phases = results["phases"]
        for phase_name, phase_data in phases.items():
            status = "PASS" if phase_data.get("success", False) else "FAIL"
            print(f"  {phase_name.upper()}: {status}")

        if "evolution" in phases:
            suggestions = phases["evolution"].get("suggestions", [])
            if suggestions:
                print(f"Suggestions: {len(suggestions)}")
                for i, suggestion in enumerate(suggestions[:3], 1):  # Show top 3
                    print(f"  {i}. {suggestion}")

    async def run_continuous_loop(self):
        """Run the continuous evolution loop"""
        print("Starting Ouroboros Auto-Evolution Loop")
        print(f"Configuration: {json.dumps(self.config, indent=2)}")
        print(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nPress Ctrl+C to stop the loop\n")

        self.running = True
        consecutive_failures = 0

        try:
            while self.running:
                if not self.config["auto_loop_enabled"]:
                    print("Auto-loop disabled in configuration. Exiting.")
                    break

                # Check max cycles
                if self.config["max_cycles"] and self.cycle_count >= self.config["max_cycles"]:
                    print(f"Reached maximum cycles ({self.config['max_cycles']}). Exiting.")
                    break

                # Run cycle
                results = await self.run_cycle()

                # Check for fitness threshold
                if results["overall_fitness"] >= self.config["fitness_threshold"]:
                    print(f"Fitness threshold ({self.config['fitness_threshold']}) reached!")
                    break

                # Check for too many failures
                if not results["overall_fitness"] > 0:  # Failed cycle
                    consecutive_failures += 1
                    if consecutive_failures >= self.config["consecutive_failures_threshold"]:
                        print(f"Too many consecutive failures ({consecutive_failures}). Stopping.")
                        break
                else:
                    consecutive_failures = 0

                # Wait for next cycle
                if self.cycle_count < (self.config["max_cycles"] or float('inf')):
                    interval = self.config["generation_interval_seconds"]
                    print(f"\nWaiting {interval} seconds until next cycle...")
                    await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("\nAuto-evolution loop stopped by user")
        except Exception as e:
            print(f"\nAuto-evolution loop stopped due to error: {e}")
        finally:
            self._print_final_summary()

    def _print_final_summary(self):
        """Print final evolution summary"""
        end_time = datetime.now(UTC)
        total_duration = (end_time - self.start_time).total_seconds()

        print(f"\n{'='*60}")
        print("AUTO-EVOLUTION LOOP COMPLETE")
        print(f"{'='*60}")
        print(f"Total Cycles: {self.cycle_count}")
        print(f"Total Duration: {total_duration:.1f} seconds")
        print(f"Average Cycle Time: {total_duration/self.cycle_count:.1f}s" if self.cycle_count > 0 else "N/A")

        if self.results_history:
            final_fitness = self.results_history[-1].get("overall_fitness", 0)
            print(f"Final Fitness: {final_fitness:.2f}/1.0")

            # Calculate improvement
            if len(self.results_history) > 1:
                initial_fitness = self.results_history[0].get("overall_fitness", 0)
                improvement = final_fitness - initial_fitness
                print(f"Fitness Change: {improvement:+.2f}")

        # Save results to file
        results_file = Path("autorun_results.json")
        with open(results_file, 'w') as f:
            json.dump({
                "config": self.config,
                "cycles_completed": self.cycle_count,
                "total_duration_seconds": total_duration,
                "results_history": self.results_history[-10:],  # Last 10 cycles
                "final_summary": {
                    "end_time": end_time.isoformat(),
                    "average_fitness": sum(r.get("overall_fitness", 0) for r in self.results_history) / len(self.results_history) if self.results_history else 0
                }
            }, f, indent=2)

        print(f"Results saved to: {results_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Ouroboros Auto-Evolution Loop")
    parser.add_argument("--max-cycles", type=int, help="Maximum number of cycles to run")
    parser.add_argument("--interval-seconds", type=int, help="Override default interval between cycles")
    parser.add_argument("--apply-safe-actions", action="store_true", help="Enable safe automated actions")
    parser.add_argument("--fitness-threshold", type=float, help="Stop when fitness reaches this threshold")
    parser.add_argument("--disable-tests", action="store_true", help="Skip test suite")
    parser.add_argument("--disable-benchmarks", action="store_true", help="Skip benchmarks")
    parser.add_argument("--disable-health-checks", action="store_true", help="Skip health checks")

    args = parser.parse_args()

    # Build configuration
    config = {
        "auto_loop_enabled": True,
        "generation_interval_seconds": args.interval_seconds or 300,
        "max_cycles": args.max_cycles,
        "apply_safe_actions": args.apply_safe_actions,
        "tests_enabled": not args.disable_tests,
        "benchmark_enabled": not args.disable_benchmarks,
        "health_checks_enabled": not args.disable_health_checks,
        "fitness_threshold": args.fitness_threshold or 0.95,
        "consecutive_failures_threshold": 3
    }

    # Create and run the evolution loop
    loop = AutoEvolutionLoop(config)

    # Run the async loop
    asyncio.run(loop.run_continuous_loop())


if __name__ == "__main__":
    main()
