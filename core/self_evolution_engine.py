"""
Self-Evolution Engine - Elite Autonomous Code Generation & Evolution

This module implements a sophisticated self-evolution system capable of:
- Contract-based evolution with safety constraints
- Autonomous code generation and refactoring
- Fitness-driven evolutionary algorithms
- Safe deployment with rollback capabilities
- Multi-objective optimization for system improvement

Key Features:
- Evolution contracts with safety boundaries
- Autonomous code generation using AI orchestration
- Fitness-based selection and mutation
- Safe deployment with comprehensive testing
- Performance tracking and optimization
- Automated rollback on failures
"""

import asyncio
import json
import hashlib
import time
import re
import ast
import inspect
from datetime import datetime, UTC, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable, Set, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from pathlib import Path
import tempfile
import subprocess
import shutil

from .orchestrator import DynamicOrchestrator
from .advanced_fitness import get_advanced_fitness_scorer
from .multi_ai_orchestrator import get_multi_ai_orchestrator, TaskComplexity

class EvolutionPhase(Enum):
    """Evolution pipeline phases."""
    ANALYSIS = "analysis"
    PLANNING = "planning"
    GENERATION = "generation"
    VALIDATION = "validation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    ROLLBACK = "rollback"

class EvolutionRisk(Enum):
    """Risk levels for evolutionary changes."""
    LOW = "low"          # Documentation, comments, minor formatting
    MEDIUM = "medium"    # Refactoring, optimization, new features
    HIGH = "high"        # Architecture changes, breaking changes
    CRITICAL = "critical" # Core system modifications, security changes

@dataclass
class EvolutionContract:
    """Safety contract defining evolution boundaries."""
    contract_id: str
    name: str
    description: str
    risk_level: EvolutionRisk

    # Safety boundaries
    allowed_files: List[str] = field(default_factory=list)  # File patterns allowed to modify
    forbidden_files: List[str] = field(default_factory=list)  # File patterns forbidden to modify
    allowed_operations: List[str] = field(default_factory=list)  # Allowed operations
    forbidden_operations: List[str] = field(default_factory=list)  # Forbidden operations

    # Performance constraints
    max_execution_time: int = 300  # Max evolution time in seconds
    max_file_changes: int = 10     # Max files that can be modified
    max_lines_changed: int = 1000  # Max lines that can be modified

    # Validation requirements
    require_tests: bool = True
    require_fitness_check: bool = True
    require_rollback_plan: bool = True

    # Evolution objectives
    target_fitness_improvement: float = 0.05  # Minimum fitness improvement required
    max_regression_allowed: float = 0.02     # Maximum allowed fitness regression

@dataclass
class EvolutionCandidate:
    """Candidate solution for evolutionary improvement."""
    candidate_id: str
    contract: EvolutionContract
    description: str
    changes: List[Dict[str, Any]] = field(default_factory=list)

    # Fitness tracking
    baseline_fitness: float = 0.0
    predicted_fitness: float = 0.0
    actual_fitness: float = 0.0

    # Evolution metadata
    generation_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    estimated_risk: EvolutionRisk = EvolutionRisk.MEDIUM
    confidence_score: float = 0.5

    # Execution tracking
    phase: EvolutionPhase = EvolutionPhase.ANALYSIS
    execution_log: List[str] = field(default_factory=list)
    success: bool = False

@dataclass
class EvolutionResult:
    """Result of an evolution attempt."""
    evolution_id: str
    candidate: EvolutionCandidate
    success: bool
    fitness_improvement: float
    execution_time: float
    changes_applied: int
    tests_passed: bool = True
    rollback_available: bool = True

    # Performance metrics
    pre_evolution_fitness: float = 0.0
    post_evolution_fitness: float = 0.0

    # Error tracking
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

class EliteSelfEvolutionEngine:
    """
    Elite Self-Evolution Engine - Autonomous Code Generation & Evolution

    Advanced evolutionary system with contract-based safety and AI-driven
    code generation for continuous system improvement.
    """

    def __init__(self, workspace_root: Path = None):
        self.logger = logging.getLogger(__name__)
        self.workspace_root = workspace_root or Path.cwd()

        # Evolution contracts
        self.evolution_contracts: Dict[str, EvolutionContract] = {}
        self._initialize_default_contracts()

        # Evolution history
        self.evolution_history: List[EvolutionResult] = []
        self.active_evolutions: Dict[str, EvolutionCandidate] = {}

        # Backup system
        self.backup_root = self.workspace_root / "evolution_backups"
        self.backup_root.mkdir(parents=True, exist_ok=True)

        # AI orchestration for code generation
        self.ai_orchestrator = None
        self.fitness_scorer = None

        # Evolution parameters
        self.max_parallel_evolutions = 3
        self.evolution_timeout = 600  # 10 minutes
        self.fitness_stabilization_time = 60  # 1 minute to stabilize

        # Safety controls
        self.emergency_stop = False
        self.max_daily_evolutions = 10
        self.daily_evolution_count = 0
        self.last_reset_date = datetime.now(UTC).date()

    async def initialize(self) -> None:
        """Initialize the self-evolution engine."""
        self.logger.info("Initializing Elite Self-Evolution Engine...")

        # Initialize AI components
        self.ai_orchestrator = await get_multi_ai_orchestrator()
        self.fitness_scorer = await get_advanced_fitness_scorer()

        # Reset daily counter if needed
        today = datetime.now(UTC).date()
        if self.last_reset_date != today:
            self.daily_evolution_count = 0
            self.last_reset_date = today

        self.logger.info("Elite Self-Evolution Engine initialized")

    async def execute_evolution_cycle(self, contract_id: str = "safe_optimization") -> EvolutionResult:
        """
        Execute a complete evolution cycle.

        Args:
            contract_id: ID of the evolution contract to use

        Returns:
            Evolution result with success metrics
        """
        if contract_id not in self.evolution_contracts:
            raise ValueError(f"Unknown evolution contract: {contract_id}")

        if self.daily_evolution_count >= self.max_daily_evolutions:
            raise Exception("Daily evolution limit reached")

        contract = self.evolution_contracts[contract_id]
        evolution_id = f"evo_{contract_id}_{int(time.time())}"

        self.logger.info(f"Starting evolution cycle: {evolution_id}")

        # Create evolution candidate
        candidate = EvolutionCandidate(
            candidate_id=evolution_id,
            contract=contract,
            description=f"Evolution cycle using {contract.name} contract"
        )

        self.active_evolutions[evolution_id] = candidate

        try:
            # Phase 1: Analysis
            candidate.phase = EvolutionPhase.ANALYSIS
            await self._analyze_system_state(candidate)

            # Phase 2: Planning
            candidate.phase = EvolutionPhase.PLANNING
            await self._plan_evolutionary_changes(candidate)

            # Phase 3: Generation
            candidate.phase = EvolutionPhase.GENERATION
            await self._generate_code_changes(candidate)

            # Phase 4: Validation
            candidate.phase = EvolutionPhase.VALIDATION
            await self._validate_changes(candidate)

            # Phase 5: Testing
            candidate.phase = EvolutionPhase.TESTING
            await self._execute_tests(candidate)

            # Phase 6: Deployment
            candidate.phase = EvolutionPhase.DEPLOYMENT
            result = await self._deploy_changes(candidate)

            # Phase 7: Monitoring
            candidate.phase = EvolutionPhase.MONITORING
            await self._monitor_post_deployment(result)

            self.daily_evolution_count += 1
            candidate.success = result.success

            self.logger.info(f"Evolution cycle completed: {evolution_id} (Success: {result.success})")
            return result

        except Exception as e:
            self.logger.error(f"Evolution cycle failed: {evolution_id} - {e}")

            # Execute rollback if possible
            await self._execute_rollback(candidate, str(e))

            return EvolutionResult(
                evolution_id=evolution_id,
                candidate=candidate,
                success=False,
                fitness_improvement=0.0,
                execution_time=time.time() - candidate.generation_time.timestamp(),
                changes_applied=0,
                errors=[str(e)]
            )

        finally:
            # Cleanup
            if evolution_id in self.active_evolutions:
                del self.active_evolutions[evolution_id]

    async def _analyze_system_state(self, candidate: EvolutionCandidate) -> None:
        """Analyze current system state for evolution opportunities."""
        candidate.execution_log.append("Phase 1: Analyzing system state...")

        # Get current fitness
        assessment = await self.fitness_scorer.assess_system_health()
        candidate.baseline_fitness = assessment.overall_score

        # Get evolution trajectory
        trajectory = await self.fitness_scorer.get_evolution_trajectory(days_ahead=7)
        candidate.predicted_fitness = trajectory.predicted_fitness

        # Analyze code quality issues
        code_issues = await self._analyze_code_quality()
        evolution_opportunities = await self._identify_evolution_opportunities(code_issues)

        candidate.execution_log.append(f"Baseline fitness: {candidate.baseline_fitness:.3f}")
        candidate.execution_log.append(f"Predicted fitness: {candidate.predicted_fitness:.3f}")
        candidate.execution_log.append(f"Evolution opportunities: {len(evolution_opportunities)}")

    async def _plan_evolutionary_changes(self, candidate: EvolutionCandidate) -> None:
        """Plan specific evolutionary changes."""
        candidate.execution_log.append("Phase 2: Planning evolutionary changes...")

        # Generate improvement plan using AI
        improvement_plan = await self._generate_improvement_plan(candidate)

        # Convert plan to specific changes
        changes = await self._plan_to_changes(improvement_plan, candidate.contract)

        # Validate against contract constraints
        await self._validate_against_contract(changes, candidate.contract)

        candidate.changes = changes
        candidate.execution_log.append(f"Planned {len(changes)} changes")

    async def _generate_code_changes(self, candidate: EvolutionCandidate) -> None:
        """Generate actual code changes using AI orchestration."""
        candidate.execution_log.append("Phase 3: Generating code changes...")

        for change in candidate.changes:
            if change['type'] == 'code_generation':
                # Use AI to generate code
                generated_code = await self._generate_code_with_ai(
                    change['description'],
                    change['context']
                )
                change['generated_code'] = generated_code

            elif change['type'] == 'refactoring':
                # Use AI to refactor existing code
                refactored_code = await self._refactor_code_with_ai(
                    change['file'],
                    change['description']
                )
                change['refactored_code'] = refactored_code

        candidate.execution_log.append("Code generation completed")

    async def _validate_changes(self, candidate: EvolutionCandidate) -> None:
        """Validate changes against safety constraints."""
        candidate.execution_log.append("Phase 4: Validating changes...")

        # Syntax validation
        for change in candidate.changes:
            if 'generated_code' in change:
                try:
                    ast.parse(change['generated_code'])
                except SyntaxError as e:
                    raise Exception(f"Syntax error in generated code: {e}")

        # Contract validation
        total_lines_changed = sum(len(change.get('generated_code', '').split('\n'))
                                for change in candidate.changes)
        files_changed = len(set(change['file'] for change in candidate.changes))

        if total_lines_changed > candidate.contract.max_lines_changed:
            raise Exception(f"Too many lines changed: {total_lines_changed} > {candidate.contract.max_lines_changed}")

        if files_changed > candidate.contract.max_file_changes:
            raise Exception(f"Too many files changed: {files_changed} > {candidate.contract.max_file_changes}")

        candidate.execution_log.append("Changes validated successfully")

    async def _execute_tests(self, candidate: EvolutionCandidate) -> None:
        """Execute comprehensive tests."""
        candidate.execution_log.append("Phase 5: Executing tests...")

        # Run existing test suite
        test_success = await self._run_test_suite()

        if not test_success and candidate.contract.require_tests:
            raise Exception("Test suite failed")

        candidate.execution_log.append(f"Tests {'passed' if test_success else 'failed'}")

    async def _deploy_changes(self, candidate: EvolutionCandidate) -> EvolutionResult:
        """Deploy changes with rollback capability."""
        candidate.execution_log.append("Phase 6: Deploying changes...")

        # Create backup
        backup_id = await self._create_backup(candidate)

        # Apply changes
        changes_applied = 0
        start_time = time.time()

        try:
            for change in candidate.changes:
                await self._apply_single_change(change)
                changes_applied += 1

            # Wait for system stabilization
            await asyncio.sleep(self.fitness_stabilization_time)

            # Measure post-deployment fitness
            post_assessment = await self.fitness_scorer.assess_system_health()
            post_fitness = post_assessment.overall_score

            fitness_improvement = post_fitness - candidate.baseline_fitness

            # Check if improvement meets contract requirements
            if fitness_improvement < candidate.contract.target_fitness_improvement:
                raise Exception(f"Insufficient fitness improvement: {fitness_improvement:.3f} < {candidate.contract.target_fitness_improvement:.3f}")

            execution_time = time.time() - start_time

            result = EvolutionResult(
                evolution_id=candidate.candidate_id,
                candidate=candidate,
                success=True,
                fitness_improvement=fitness_improvement,
                execution_time=execution_time,
                changes_applied=changes_applied,
                pre_evolution_fitness=candidate.baseline_fitness,
                post_evolution_fitness=post_fitness
            )

            self.evolution_history.append(result)
            candidate.execution_log.append(f"Deployment successful - Fitness improved by {fitness_improvement:.3f}")

            return result

        except Exception as e:
            # Rollback on failure
            await self._rollback_to_backup(backup_id)
            raise e

    async def _monitor_post_deployment(self, result: EvolutionResult) -> None:
        """Monitor system after deployment."""
        # Monitor for 5 minutes to ensure stability
        monitoring_start = time.time()

        while time.time() - monitoring_start < 300:  # 5 minutes
            assessment = await self.fitness_scorer.assess_system_health()

            # Check for significant regression
            regression = result.pre_evolution_fitness - assessment.overall_score
            if regression > result.candidate.contract.max_regression_allowed:
                self.logger.warning(f"Significant regression detected: {regression:.3f}")
                # Could trigger automatic rollback here

            await asyncio.sleep(30)  # Check every 30 seconds

    def _initialize_default_contracts(self) -> None:
        """Initialize default evolution contracts."""
        self.evolution_contracts = {
            "safe_optimization": EvolutionContract(
                contract_id="safe_optimization",
                name="Safe Optimization",
                description="Safe code optimizations without breaking changes",
                risk_level=EvolutionRisk.LOW,
                allowed_files=["*.py"],
                forbidden_files=["*test*.py", "*__init__.py", "*config*.py"],
                allowed_operations=["optimize", "refactor", "add_comments"],
                forbidden_operations=["delete", "security_changes"],
                max_file_changes=3,
                max_lines_changed=200,
                require_tests=True,
                target_fitness_improvement=0.02
            ),

            "feature_enhancement": EvolutionContract(
                contract_id="feature_enhancement",
                name="Feature Enhancement",
                description="Add new features with medium risk",
                risk_level=EvolutionRisk.MEDIUM,
                allowed_files=["*.py"],
                forbidden_files=["*security*.py", "*auth*.py"],
                allowed_operations=["add_feature", "refactor", "optimize"],
                max_file_changes=5,
                max_lines_changed=500,
                target_fitness_improvement=0.05
            ),

            "architecture_improvement": EvolutionContract(
                contract_id="architecture_improvement",
                name="Architecture Improvement",
                description="Major architectural changes",
                risk_level=EvolutionRisk.HIGH,
                allowed_files=["*.py"],
                forbidden_files=["*critical*.py"],
                allowed_operations=["architectural_change", "refactor"],
                max_file_changes=10,
                max_lines_changed=1000,
                target_fitness_improvement=0.10,
                max_regression_allowed=0.05
            )
        }

    async def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality for evolution opportunities."""
        # This would integrate with code analysis tools
        # For now, return mock analysis
        return {
            "complexity_issues": 5,
            "unused_imports": 3,
            "code_duplication": 2,
            "performance_bottlenecks": 1
        }

    async def _identify_evolution_opportunities(self, code_issues: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific evolution opportunities."""
        opportunities = []

        if code_issues.get("complexity_issues", 0) > 0:
            opportunities.append({
                "type": "refactoring",
                "description": "Reduce code complexity",
                "impact": "medium"
            })

        if code_issues.get("performance_bottlenecks", 0) > 0:
            opportunities.append({
                "type": "optimization",
                "description": "Optimize performance bottlenecks",
                "impact": "high"
            })

        return opportunities

    async def _generate_improvement_plan(self, candidate: EvolutionCandidate) -> Dict[str, Any]:
        """Generate improvement plan using AI."""
        prompt = f"""
        Analyze the current system state and generate an improvement plan.

        Current fitness: {candidate.baseline_fitness:.3f}
        Target improvement: {candidate.contract.target_fitness_improvement:.3f}
        Risk level: {candidate.contract.risk_level.value}

        Generate a specific, actionable improvement plan that will improve system fitness.
        Focus on {candidate.contract.allowed_operations} operations.
        """

        result = await self.ai_orchestrator.execute_task(
            prompt=prompt,
            complexity=TaskComplexity.MODERATE,
            required_capabilities={"coding": 0.8, "reasoning": 0.9}
        )

        return {"plan": result.final_answer}

    async def _plan_to_changes(self, plan: Dict[str, Any], contract: EvolutionContract) -> List[Dict[str, Any]]:
        """Convert improvement plan to specific changes."""
        # This would parse the AI-generated plan into specific file changes
        # For now, return mock changes
        return [
            {
                "type": "refactoring",
                "file": "core/orchestrator.py",
                "description": "Optimize agent discovery algorithm",
                "operation": "refactor"
            }
        ]

    async def _validate_against_contract(self, changes: List[Dict[str, Any]], contract: EvolutionContract) -> None:
        """Validate changes against contract constraints."""
        for change in changes:
            file_path = change['file']

            # Check forbidden files
            for forbidden in contract.forbidden_files:
                if Path(file_path).match(forbidden):
                    raise Exception(f"Change to forbidden file: {file_path}")

            # Check forbidden operations
            if change.get('operation') in contract.forbidden_operations:
                raise Exception(f"Forbidden operation: {change['operation']}")

    async def _generate_code_with_ai(self, description: str, context: Dict[str, Any]) -> str:
        """Generate code using AI orchestration."""
        prompt = f"Generate Python code for: {description}\n\nContext: {context}"

        result = await self.ai_orchestrator.execute_task(
            prompt=prompt,
            complexity=TaskComplexity.MODERATE,
            required_capabilities={"coding": 0.9}
        )

        return result.final_answer

    async def _refactor_code_with_ai(self, file_path: str, description: str) -> str:
        """Refactor existing code using AI."""
        # Read current file
        with open(file_path, 'r') as f:
            current_code = f.read()

        prompt = f"Refactor this Python code with the following improvement: {description}\n\nCode:\n{current_code}"

        result = await self.ai_orchestrator.execute_task(
            prompt=prompt,
            complexity=TaskComplexity.MODERATE,
            required_capabilities={"coding": 0.8, "reasoning": 0.8}
        )

        return result.final_answer

    async def _run_test_suite(self) -> bool:
        """Run the test suite."""
        try:
            # Run pytest
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _create_backup(self, candidate: EvolutionCandidate) -> str:
        """Create backup before changes."""
        backup_id = f"backup_{candidate.candidate_id}"
        backup_path = self.backup_root / backup_id
        backup_path.mkdir()

        # Backup changed files
        for change in candidate.changes:
            file_path = Path(change['file'])
            if file_path.exists():
                backup_file = backup_path / file_path.name
                shutil.copy2(file_path, backup_file)

        return backup_id

    async def _apply_single_change(self, change: Dict[str, Any]) -> None:
        """Apply a single change to the codebase."""
        file_path = Path(change['file'])

        if change['type'] == 'refactoring':
            # Replace file content
            with open(file_path, 'w') as f:
                f.write(change['refactored_code'])
        elif change['type'] == 'code_generation':
            # Append to file (simplified)
            with open(file_path, 'a') as f:
                f.write(f"\n\n# Auto-generated improvement\n{change['generated_code']}")

    async def _rollback_to_backup(self, backup_id: str) -> None:
        """Rollback to backup."""
        backup_path = self.backup_root / backup_id

        if backup_path.exists():
            # Restore files from backup
            for backup_file in backup_path.glob("*"):
                original_name = backup_file.stem  # Remove backup suffix if any
                original_path = self.workspace_root / original_name
                shutil.copy2(backup_file, original_path)

    async def _execute_rollback(self, candidate: EvolutionCandidate, error: str) -> None:
        """Execute emergency rollback."""
        candidate.phase = EvolutionPhase.ROLLBACK
        candidate.execution_log.append(f"ROLLBACK: {error}")

        # Find latest successful evolution
        successful_evolutions = [e for e in self.evolution_history if e.success]
        if successful_evolutions:
            latest_success = max(successful_evolutions, key=lambda e: e.evolution_id)
            await self._rollback_to_backup(f"backup_{latest_success.evolution_id}")

        candidate.execution_log.append("Rollback completed")

    async def get_evolution_statistics(self) -> Dict[str, Any]:
        """Get evolution statistics."""
        total_evolutions = len(self.evolution_history)
        successful_evolutions = sum(1 for e in self.evolution_history if e.success)

        if total_evolutions > 0:
            success_rate = successful_evolutions / total_evolutions
            avg_improvement = sum(e.fitness_improvement for e in self.evolution_history) / total_evolutions
        else:
            success_rate = 0.0
            avg_improvement = 0.0

        return {
            "total_evolutions": total_evolutions,
            "successful_evolutions": successful_evolutions,
            "success_rate": success_rate,
            "average_improvement": avg_improvement,
            "active_evolutions": len(self.active_evolutions),
            "available_contracts": len(self.evolution_contracts)
        }

    async def shutdown(self) -> None:
        """Shutdown the evolution engine."""
        self.logger.info("Shutting down Elite Self-Evolution Engine...")

        # Cancel active evolutions
        for candidate in self.active_evolutions.values():
            candidate.execution_log.append("EVOLUTION CANCELLED: Engine shutdown")

        self.active_evolutions.clear()
        self.logger.info("Elite Self-Evolution Engine shutdown complete")


# Global evolution engine instance
_evolution_engine: Optional[EliteSelfEvolutionEngine] = None

async def get_evolution_engine() -> EliteSelfEvolutionEngine:
    """Get or create global evolution engine instance."""
    global _evolution_engine
    if _evolution_engine is None:
        _evolution_engine = EliteSelfEvolutionEngine()
        await _evolution_engine.initialize()
    return _evolution_engine
