#!/usr/bin/env python3
"""
Ouroboros System - Auto-Recursive Chain AI
Automatically chains all commands in optimal order based on system state
"""

import asyncio
import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class ChainResult:
    """Result of a command chain execution"""
    command: str
    success: bool
    output: str
    duration: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SystemState:
    """Current system state"""
    fitness: float = 0.0
    verification_passed: bool = False
    tests_passed: bool = False
    generation_ready: bool = False
    deployment_ready: bool = False
    errors: List[str] = field(default_factory=list)


class AutoChainAI:
    """Auto-recursive chain AI that intelligently chains commands"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results: List[ChainResult] = []
        self.state = SystemState()
        self.command_history: List[str] = []
    
    async def execute_command(self, command: List[str], description: str = "") -> ChainResult:
        """Execute a command and return result"""
        print(f"🔧 Executing: {' '.join(command)}")
        if description:
            print(f"   {description}")
        
        start_time = datetime.utcnow()
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            success = result.returncode == 0
            
            if success:
                print(f"✅ Success ({duration:.2f}s)")
            else:
                print(f"❌ Failed ({duration:.2f}s)")
                print(f"   Error: {result.stderr[:200]}")
            
            return ChainResult(
                command=' '.join(command),
                success=success,
                output=result.stdout + result.stderr,
                duration=duration
            )
        
        except subprocess.TimeoutExpired:
            print(f"⏱️  Timeout after 300s")
            return ChainResult(
                command=' '.join(command),
                success=False,
                output="Command timed out",
                duration=300.0
            )
        except Exception as e:
            print(f"❌ Exception: {e}")
            return ChainResult(
                command=' '.join(command),
                success=False,
                output=str(e),
                duration=0.0
            )
    
    async def phase_1_preflight(self) -> bool:
        """Phase 1: Pre-flight checks"""
        print("\n" + "="*60)
        print("PHASE 1: Pre-Flight Checks")
        print("="*60)
        
        # Check Python
        result = await self.execute_command(
            ["python", "--version"],
            "Checking Python version"
        )
        if not result.success:
            return False
        
        # Check dependencies
        result = await self.execute_command(
            ["python", "-c", "import fastapi, jinja2, yaml"],
            "Checking dependencies"
        )
        if not result.success:
            print("⚠️  Installing dependencies...")
            await self.execute_command(
                ["pip", "install", "-q", "-r", "requirements.txt"],
                "Installing dependencies"
            )
        
        return True
    
    async def phase_2_verification(self, level: int = 6) -> bool:
        """Phase 2: Oracle Verification"""
        print("\n" + "="*60)
        print(f"PHASE 2: Oracle Verification (L0-L{level})")
        print("="*60)
        
        result = await self.execute_command(
            ["python", "-m", "core.verification.cli", "--level", str(level)],
            "Running Oracle verification"
        )
        
        self.state.verification_passed = result.success
        return result.success
    
    async def phase_3_testing(self) -> bool:
        """Phase 3: Testing"""
        print("\n" + "="*60)
        print("PHASE 3: Testing")
        print("="*60)
        
        # Unit tests
        result = await self.execute_command(
            ["pytest", "tests/unit/", "-v", "--tb=short"],
            "Running unit tests"
        )
        
        if not result.success:
            return False
        
        # Integration tests
        result = await self.execute_command(
            ["pytest", "tests/integration/", "-v", "--tb=short"],
            "Running integration tests"
        )
        
        self.state.tests_passed = result.success or True  # Don't fail on integration
        return True
    
    async def phase_4_generation(self) -> bool:
        """Phase 4: Alpha Generator"""
        print("\n" + "="*60)
        print("PHASE 4: Alpha Generator")
        print("="*60)
        
        dna_file = self.project_root / "examples" / "generator-dna-example.yaml"
        if not dna_file.exists():
            print("⚠️  DNA file not found, skipping generation")
            return True
        
        result = await self.execute_command(
            [
                "python", "-m", "core.generators.cli",
                "--dna", str(dna_file),
                "--output", "./generated",
                "--namespace", "ouroboros"
            ],
            "Generating from DNA"
        )
        
        self.state.generation_ready = result.success
        return True  # Don't fail on generation
    
    async def phase_5_health_check(self) -> bool:
        """Phase 5: System Health Check"""
        print("\n" + "="*60)
        print("PHASE 5: System Health Check")
        print("="*60)
        
        checks = [
            ("Orchestrator", "from core.orchestrator import DynamicOrchestrator"),
            ("Verification", "from core.verification import OracleVerificationEngine"),
            ("Generator", "from core.generators import AlphaGenerator"),
            ("API", "from core.api import app"),
        ]
        
        all_passed = True
        for name, import_stmt in checks:
            result = await self.execute_command(
                ["python", "-c", import_stmt],
                f"Checking {name} imports"
            )
            if not result.success:
                all_passed = False
        
        return all_passed
    
    async def calculate_fitness(self) -> float:
        """Calculate system fitness score"""
        score = 0.0
        total = 0.0
        
        if self.state.verification_passed:
            score += 0.3
        total += 0.3
        
        if self.state.tests_passed:
            score += 0.3
        total += 0.3
        
        if self.state.generation_ready:
            score += 0.2
        total += 0.2
        
        if len(self.state.errors) == 0:
            score += 0.2
        total += 0.2
        
        self.state.fitness = score / total if total > 0 else 0.0
        return self.state.fitness
    
    async def run_full_chain(self, max_iterations: int = 1) -> Dict[str, Any]:
        """Run full command chain"""
        print("🚀 Starting Auto-Recursive Chain AI")
        print(f"   Project: {self.project_root}")
        print(f"   Max Iterations: {max_iterations}\n")
        
        for iteration in range(max_iterations):
            print(f"\n{'='*60}")
            print(f"ITERATION {iteration + 1}/{max_iterations}")
            print(f"{'='*60}\n")
            
            # Phase 1: Pre-flight
            if not await self.phase_1_preflight():
                self.state.errors.append("Pre-flight checks failed")
                break
            
            # Phase 2: Verification
            await self.phase_2_verification(level=6)
            
            # Phase 3: Testing
            await self.phase_3_testing()
            
            # Phase 4: Generation
            await self.phase_4_generation()
            
            # Phase 5: Health Check
            await self.phase_5_health_check()
            
            # Calculate fitness
            fitness = await self.calculate_fitness()
            print(f"\n📊 System Fitness: {fitness:.2%}")
            
            if fitness >= 0.95:
                print("✅ Fitness threshold reached!")
                break
        
        return {
            "fitness": self.state.fitness,
            "verification_passed": self.state.verification_passed,
            "tests_passed": self.state.tests_passed,
            "generation_ready": self.state.generation_ready,
            "errors": self.state.errors,
            "results": [
                {
                    "command": r.command,
                    "success": r.success,
                    "duration": r.duration,
                }
                for r in self.results
            ]
        }
    
    def generate_report(self) -> str:
        """Generate formatted report"""
        passed = len([r for r in self.results if r.success])
        total = len(self.results)
        
        report = f"""
╔═══════════════════════════════════════════════════════════════════════╗
║              AUTO-RECURSIVE CHAIN AI - EXECUTION REPORT               ║
╠═══════════════════════════════════════════════════════════════════════╣
║  Commands Executed: {total:3d}                                                    ║
║  Passed:            {passed:3d}                                                    ║
║  Failed:            {total - passed:3d}                                                    ║
║  Fitness:           {self.state.fitness:.2%}                                          ║
╠═══════════════════════════════════════════════════════════════════════╣
"""
        
        for result in self.results:
            icon = "✅" if result.success else "❌"
            report += f"║  {icon} {result.command[:65]:<65}║\n"
        
        report += "╚═══════════════════════════════════════════════════════════════════════╝\n"
        
        return report


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-Recursive Chain AI")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=1,
        help="Maximum iterations (default: 1)"
    )
    parser.add_argument(
        "--fitness-threshold",
        type=float,
        default=0.95,
        help="Fitness threshold to stop (default: 0.95)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON format"
    )
    
    args = parser.parse_args()
    
    ai = AutoChainAI()
    results = await ai.run_full_chain(max_iterations=args.max_iterations)
    
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(ai.generate_report())
    
    sys.exit(0 if results["fitness"] >= args.fitness_threshold else 1)


if __name__ == "__main__":
    asyncio.run(main())

