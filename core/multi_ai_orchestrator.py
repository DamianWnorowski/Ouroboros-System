"""
Multi-AI Orchestration System - Elite AI Coordination Framework

This module implements a sophisticated multi-AI orchestration system capable of:
- Dynamic model selection based on task requirements
- Load balancing across multiple AI providers
- Intelligent routing and failover
- Performance optimization and cost management
- Real-time adaptation to model capabilities

Key Features:
- 10+ AI model support (Claude, GPT-4, GPT-3.5, Gemini, etc.)
- Automatic model selection based on task complexity
- Parallel execution for complex tasks
- Cost optimization and rate limiting
- Performance monitoring and analytics
- Automatic failover and degradation
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime, UTC, timedelta
from typing import Dict, List, Any, Optional, Union, Callable, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import aiohttp
import backoff
from concurrent.futures import ThreadPoolExecutor
import statistics
import numpy as np
from collections import defaultdict, deque

class AIModel(Enum):
    """Supported AI models with their capabilities."""
    CLAUDE_OPUS = "claude-3-opus-20240229"
    CLAUDE_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_HAIKU = "claude-3-haiku-20240307"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"
    MIXTRAL_8X7B = "mixtral-8x7b-instruct"
    LLAMA_2_70B = "llama-2-70b-chat"

class TaskComplexity(Enum):
    """Task complexity levels for model selection."""
    TRIVIAL = "trivial"      # Simple questions, basic tasks
    SIMPLE = "simple"        # Straightforward analysis, basic coding
    MODERATE = "moderate"    # Complex analysis, intermediate coding
    COMPLEX = "complex"      # Multi-step reasoning, advanced coding
    ENTERPRISE = "enterprise" # System design, architecture, strategic planning

class ExecutionMode(Enum):
    """Multi-AI execution modes."""
    SPECIALIST = "specialist"      # Single best model
    SEQUENTIAL = "sequential"      # Ordered chain execution
    PARALLEL = "parallel"          # All models simultaneously
    FEEDBACK_LOOP = "feedback"     # Iterative refinement

@dataclass
class AIModelCapabilities:
    """Capabilities and performance metrics for an AI model."""
    model: AIModel
    provider: str
    context_window: int
    max_tokens: int
    cost_per_token: float
    cost_per_request: float = 0.0

    # Performance metrics
    avg_response_time: float = 0.0
    success_rate: float = 1.0
    quality_score: float = 0.8

    # Specialized capabilities
    coding_excellence: float = 0.7
    reasoning_depth: float = 0.7
    creativity: float = 0.6
    speed: float = 0.7

    # Rate limiting
    requests_per_minute: int = 60
    tokens_per_minute: int = 100000

    # Current load
    current_requests: int = 0
    current_tokens: int = 0
    last_request_time: datetime = field(default_factory=lambda: datetime.now(UTC))

@dataclass
class AITask:
    """Represents a task to be executed by AI models."""
    id: str
    prompt: str
    complexity: TaskComplexity
    required_capabilities: Dict[str, float] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    max_tokens: int = 4000
    temperature: float = 0.7
    priority: int = 1  # 1-10, higher = more important

    # Execution tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_mode: ExecutionMode = ExecutionMode.SPECIALIST

    # Results
    responses: List[Dict[str, Any]] = field(default_factory=list)
    final_response: Optional[Dict[str, Any]] = None
    cost: float = 0.0
    quality_score: float = 0.0

@dataclass
class OrchestrationResult:
    """Result of a multi-AI orchestration task."""
    task_id: str
    execution_mode: ExecutionMode
    models_used: List[str]
    total_cost: float
    total_time: float
    quality_score: float
    responses: List[Dict[str, Any]]
    final_answer: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class ModelSelector:
    """Intelligent model selection engine."""

    def __init__(self):
        self.model_capabilities = self._initialize_model_capabilities()
        self.performance_history: Dict[AIModel, deque] = defaultdict(lambda: deque(maxlen=100))

    def _initialize_model_capabilities(self) -> Dict[AIModel, AIModelCapabilities]:
        """Initialize capabilities for all supported models."""
        return {
            AIModel.CLAUDE_OPUS: AIModelCapabilities(
                model=AIModel.CLAUDE_OPUS,
                provider="anthropic",
                context_window=200000,
                max_tokens=4096,
                cost_per_token=0.000015,
                coding_excellence=0.95,
                reasoning_depth=0.95,
                creativity=0.85,
                speed=0.7
            ),
            AIModel.CLAUDE_SONNET: AIModelCapabilities(
                model=AIModel.CLAUDE_SONNET,
                provider="anthropic",
                context_window=200000,
                max_tokens=4096,
                cost_per_token=0.000003,
                coding_excellence=0.90,
                reasoning_depth=0.90,
                creativity=0.80,
                speed=0.8
            ),
            AIModel.CLAUDE_HAIKU: AIModelCapabilities(
                model=AIModel.CLAUDE_HAIKU,
                provider="anthropic",
                context_window=200000,
                max_tokens=4096,
                cost_per_token=0.00000025,
                coding_excellence=0.80,
                reasoning_depth=0.75,
                creativity=0.70,
                speed=0.95
            ),
            AIModel.GPT_4_TURBO: AIModelCapabilities(
                model=AIModel.GPT_4_TURBO,
                provider="openai",
                context_window=128000,
                max_tokens=4096,
                cost_per_token=0.00001,
                coding_excellence=0.92,
                reasoning_depth=0.92,
                creativity=0.88,
                speed=0.75
            ),
            AIModel.GPT_4: AIModelCapabilities(
                model=AIModel.GPT_4,
                provider="openai",
                context_window=8192,
                max_tokens=4096,
                cost_per_token=0.00003,
                coding_excellence=0.95,
                reasoning_depth=0.95,
                creativity=0.85,
                speed=0.6
            ),
            AIModel.GPT_35_TURBO: AIModelCapabilities(
                model=AIModel.GPT_35_TURBO,
                provider="openai",
                context_window=16384,
                max_tokens=4096,
                cost_per_token=0.000002,
                coding_excellence=0.75,
                reasoning_depth=0.70,
                creativity=0.75,
                speed=0.9
            ),
            AIModel.GEMINI_PRO: AIModelCapabilities(
                model=AIModel.GEMINI_PRO,
                provider="google",
                context_window=32768,
                max_tokens=4096,
                cost_per_token=0.000001,
                coding_excellence=0.80,
                reasoning_depth=0.80,
                creativity=0.85,
                speed=0.85
            ),
            AIModel.GEMINI_ULTRA: AIModelCapabilities(
                model=AIModel.GEMINI_ULTRA,
                provider="google",
                context_window=32768,
                max_tokens=4096,
                cost_per_token=0.000005,
                coding_excellence=0.88,
                reasoning_depth=0.88,
                creativity=0.90,
                speed=0.75
            ),
            AIModel.MIXTRAL_8X7B: AIModelCapabilities(
                model=AIModel.MIXTRAL_8X7B,
                provider="mistral",
                context_window=32768,
                max_tokens=4096,
                cost_per_token=0.0000007,
                coding_excellence=0.82,
                reasoning_depth=0.85,
                creativity=0.78,
                speed=0.88
            ),
            AIModel.LLAMA_2_70B: AIModelCapabilities(
                model=AIModel.LLAMA_2_70B,
                provider="meta",
                context_window=4096,
                max_tokens=4096,
                cost_per_token=0.000001,
                coding_excellence=0.78,
                reasoning_depth=0.82,
                creativity=0.75,
                speed=0.82
            )
        }

    def select_models_for_task(self, task: AITask) -> List[AIModel]:
        """
        Select optimal models for a given task based on complexity and requirements.

        Returns:
            List of models to use, ordered by preference
        """
        # Determine execution mode based on complexity
        if task.complexity == TaskComplexity.TRIVIAL:
            task.execution_mode = ExecutionMode.SPECIALIST
            return [self._select_single_best_model(task)]
        elif task.complexity == TaskComplexity.SIMPLE:
            task.execution_mode = ExecutionMode.SPECIALIST
            return [self._select_single_best_model(task)]
        elif task.complexity == TaskComplexity.MODERATE:
            task.execution_mode = ExecutionMode.SEQUENTIAL
            return self._select_sequential_chain(task)
        elif task.complexity == TaskComplexity.COMPLEX:
            task.execution_mode = ExecutionMode.PARALLEL
            return self._select_parallel_swarm(task)
        else:  # ENTERPRISE
            task.execution_mode = ExecutionMode.FEEDBACK_LOOP
            return self._select_feedback_loop_models(task)

    def _select_single_best_model(self, task: AITask) -> AIModel:
        """Select the single best model for a task."""
        scores = {}

        for model, caps in self.model_capabilities.items():
            if not self._check_rate_limits(caps):
                continue

            score = self._calculate_fitness_score(task, caps)
            scores[model] = score

        if not scores:
            # Fallback to cheapest available model
            return min(
                [m for m, c in self.model_capabilities.items() if self._check_rate_limits(c)],
                key=lambda m: self.model_capabilities[m].cost_per_token
            )

        return max(scores, key=scores.get)

    def _select_sequential_chain(self, task: AITask) -> List[AIModel]:
        """Select models for sequential execution (2-3 models)."""
        # Start with best reasoning model, then coding specialist, then fast model for refinement
        candidates = [m for m, c in self.model_capabilities.items() if self._check_rate_limits(c)]

        if len(candidates) < 2:
            return candidates

        # Primary: Best reasoning
        primary = max(candidates, key=lambda m: self.model_capabilities[m].reasoning_depth)

        # Secondary: Best coding if coding task
        if task.required_capabilities.get('coding', 0) > 0.7:
            secondary = max(candidates, key=lambda m: self.model_capabilities[m].coding_excellence)
        else:
            secondary = max(candidates, key=lambda m: self.model_capabilities[m].creativity)

        # Tertiary: Fast model for final polish
        tertiary = max(candidates, key=lambda m: self.model_capabilities[m].speed)

        result = [primary]
        if secondary != primary:
            result.append(secondary)
        if tertiary not in result:
            result.append(tertiary)

        return result[:3]

    def _select_parallel_swarm(self, task: AITask) -> List[AIModel]:
        """Select models for parallel execution (3-5 models)."""
        candidates = [m for m, c in self.model_capabilities.items() if self._check_rate_limits(c)]

        if len(candidates) <= 3:
            return candidates

        # Select diverse models with different strengths
        selected = []
        remaining = candidates.copy()

        # Always include top performer
        best = max(remaining, key=lambda m: self._calculate_fitness_score(task, self.model_capabilities[m]))
        selected.append(best)
        remaining.remove(best)

        # Add models with complementary strengths
        for _ in range(min(4, len(remaining))):
            if not remaining:
                break

            # Select most different from already selected
            next_model = max(remaining, key=lambda m: self._diversity_score(m, selected, task))
            selected.append(next_model)
            remaining.remove(next_model)

        return selected

    def _select_feedback_loop_models(self, task: AITask) -> List[AIModel]:
        """Select models for iterative feedback loop."""
        # Use top 3 models for enterprise tasks
        candidates = [m for m, c in self.model_capabilities.items() if self._check_rate_limits(c)]
        return sorted(candidates,
                     key=lambda m: self._calculate_fitness_score(task, self.model_capabilities[m]),
                     reverse=True)[:3]

    def _calculate_fitness_score(self, task: AITask, caps: AIModelCapabilities) -> float:
        """Calculate how well a model fits a task."""
        score = 0.0

        # Base capabilities match
        for capability, weight in task.required_capabilities.items():
            if hasattr(caps, capability):
                model_value = getattr(caps, capability)
                score += weight * model_value

        # Cost efficiency (inverse of cost, normalized)
        cost_score = 1.0 / (1.0 + caps.cost_per_token * 1000)
        score += 0.2 * cost_score

        # Speed preference for simple tasks
        if task.complexity in [TaskComplexity.TRIVIAL, TaskComplexity.SIMPLE]:
            score += 0.3 * caps.speed

        # Quality preference for complex tasks
        if task.complexity in [TaskComplexity.COMPLEX, TaskComplexity.ENTERPRISE]:
            score += 0.3 * (caps.reasoning_depth + caps.quality_score) / 2

        # Performance history bonus
        if caps.model in self.performance_history:
            recent_scores = list(self.performance_history[caps.model])
            if recent_scores:
                avg_performance = statistics.mean(recent_scores)
                score += 0.1 * avg_performance

        return score

    def _diversity_score(self, candidate: AIModel, selected: List[AIModel], task: AITask) -> float:
        """Calculate diversity score for parallel execution."""
        if not selected:
            return self._calculate_fitness_score(task, self.model_capabilities[candidate])

        # Average difference in capabilities
        candidate_caps = self.model_capabilities[candidate]
        avg_differences = []

        for selected_model in selected:
            selected_caps = self.model_capabilities[selected_model]

            differences = []
            for attr in ['coding_excellence', 'reasoning_depth', 'creativity', 'speed']:
                diff = abs(getattr(candidate_caps, attr) - getattr(selected_caps, attr))
                differences.append(diff)

            avg_differences.append(statistics.mean(differences))

        # Higher diversity = higher score
        return statistics.mean(avg_differences)

    def _check_rate_limits(self, caps: AIModelCapabilities) -> bool:
        """Check if model is within rate limits."""
        now = datetime.now(UTC)

        # Reset counters if minute has passed
        if (now - caps.last_request_time).total_seconds() > 60:
            caps.current_requests = 0
            caps.current_tokens = 0

        return (caps.current_requests < caps.requests_per_minute and
                caps.current_tokens < caps.tokens_per_minute)

class MultiAIOrchestrator:
    """
    Elite Multi-AI Orchestration System

    Coordinates multiple AI models for optimal task execution with:
    - Intelligent model selection
    - Load balancing and rate limiting
    - Parallel and sequential execution
    - Cost optimization
    - Performance monitoring
    - Automatic failover
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model_selector = ModelSelector()
        self.active_tasks: Dict[str, AITask] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)

        # API clients (would be initialized with actual API keys)
        self.api_clients: Dict[str, Any] = {}

        # Performance tracking
        self.task_history: deque = deque(maxlen=1000)
        self.cost_tracking: Dict[str, float] = defaultdict(float)

        # Load balancing
        self.model_load: Dict[AIModel, int] = defaultdict(int)

    async def initialize(self) -> None:
        """Initialize the multi-AI orchestrator."""
        self.logger.info("Initializing Multi-AI Orchestrator...")

        # Initialize API clients (placeholder - would use actual API keys)
        await self._init_api_clients()

        # Start performance monitoring
        asyncio.create_task(self._performance_monitoring_loop())

        self.logger.info("Multi-AI Orchestrator initialized")

    async def execute_task(self, prompt: str, complexity: TaskComplexity = None,
                          required_capabilities: Dict[str, float] = None,
                          context: Dict[str, Any] = None,
                          priority: int = 1) -> OrchestrationResult:
        """
        Execute a task using optimal AI orchestration.

        Args:
            prompt: The task prompt
            complexity: Task complexity (auto-detected if None)
            required_capabilities: Specific capability requirements
            context: Additional context
            priority: Task priority (1-10)

        Returns:
            OrchestrationResult with execution details
        """
        # Auto-detect complexity if not provided
        if complexity is None:
            complexity = self._detect_complexity(prompt)

        # Create task
        task_id = f"task_{hashlib.md5(prompt.encode()).hexdigest()[:16]}"
        task = AITask(
            id=task_id,
            prompt=prompt,
            complexity=complexity,
            required_capabilities=required_capabilities or {},
            context=context or {},
            priority=priority
        )

        self.active_tasks[task_id] = task
        task.started_at = datetime.now(UTC)

        try:
            # Select models for execution
            selected_models = self.model_selector.select_models_for_task(task)

            if not selected_models:
                raise Exception("No suitable models available for task")

            # Execute based on mode
            if task.execution_mode == ExecutionMode.SPECIALIST:
                result = await self._execute_specialist(task, selected_models[0])
            elif task.execution_mode == ExecutionMode.SEQUENTIAL:
                result = await self._execute_sequential(task, selected_models)
            elif task.execution_mode == ExecutionMode.PARALLEL:
                result = await self._execute_parallel(task, selected_models)
            else:  # FEEDBACK_LOOP
                result = await self._execute_feedback_loop(task, selected_models)

            # Update performance metrics
            await self._update_performance_metrics(task, result)

            task.completed_at = datetime.now(UTC)
            task.cost = result.total_cost
            task.quality_score = result.quality_score

            return result

        finally:
            # Cleanup
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]

    async def _execute_specialist(self, task: AITask, model: AIModel) -> OrchestrationResult:
        """Execute task with single best model."""
        start_time = time.time()

        try:
            response = await self._call_model_api(model, task.prompt, task.max_tokens, task.temperature)
            total_time = time.time() - start_time

            result = OrchestrationResult(
                task_id=task.id,
                execution_mode=ExecutionMode.SPECIALIST,
                models_used=[model.value],
                total_cost=self._calculate_cost(model, response),
                total_time=total_time,
                quality_score=self._evaluate_response_quality(response),
                responses=[response],
                final_answer=response.get('content', ''),
                metadata={'model': model.value}
            )

            return result

        except Exception as e:
            self.logger.error(f"Specialist execution failed: {e}")
            raise

    async def _execute_sequential(self, task: AITask, models: List[AIModel]) -> OrchestrationResult:
        """Execute task with sequential model chain."""
        start_time = time.time()
        responses = []
        total_cost = 0.0

        current_prompt = task.prompt

        for i, model in enumerate(models):
            try:
                # Enhance prompt with previous responses for subsequent models
                if i > 0:
                    previous_responses = "\n\n".join([
                        f"Model {prev_model.value}: {resp.get('content', '')}"
                        for prev_model, resp in zip(models[:i], responses)
                    ])
                    current_prompt = f"{task.prompt}\n\nPrevious model responses:\n{previous_responses}\n\nPlease build upon and improve this analysis:"

                response = await self._call_model_api(model, current_prompt, task.max_tokens, task.temperature)
                responses.append(response)
                total_cost += self._calculate_cost(model, response)

            except Exception as e:
                self.logger.warning(f"Model {model.value} failed in sequential chain: {e}")
                continue

        total_time = time.time() - start_time

        # Use final response as answer
        final_answer = responses[-1].get('content', '') if responses else ''

        result = OrchestrationResult(
            task_id=task.id,
            execution_mode=ExecutionMode.SEQUENTIAL,
            models_used=[m.value for m in models],
            total_cost=total_cost,
            total_time=total_time,
            quality_score=self._evaluate_response_quality(responses[-1] if responses else {}),
            responses=responses,
            final_answer=final_answer,
            metadata={'chain_length': len(responses)}
        )

        return result

    async def _execute_parallel(self, task: AITask, models: List[AIModel]) -> OrchestrationResult:
        """Execute task with parallel model swarm."""
        start_time = time.time()

        # Execute all models in parallel
        tasks = [
            self._call_model_api(model, task.prompt, task.max_tokens, task.temperature)
            for model in models
        ]

        try:
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            self.logger.error(f"Parallel execution failed: {e}")
            responses = []

        # Filter out exceptions and calculate costs
        valid_responses = []
        total_cost = 0.0

        for model, response in zip(models, responses):
            if isinstance(response, Exception):
                self.logger.warning(f"Model {model.value} failed: {response}")
                continue

            valid_responses.append(response)
            total_cost += self._calculate_cost(model, response)

        total_time = time.time() - start_time

        # Aggregate responses (simple concatenation for now)
        final_answer = self._aggregate_responses(valid_responses)

        result = OrchestrationResult(
            task_id=task.id,
            execution_mode=ExecutionMode.PARALLEL,
            models_used=[m.value for m in models],
            total_cost=total_cost,
            total_time=total_time,
            quality_score=self._evaluate_response_quality(valid_responses[0] if valid_responses else {}),
            responses=valid_responses,
            final_answer=final_answer,
            metadata={'parallel_count': len(valid_responses)}
        )

        return result

    async def _execute_feedback_loop(self, task: AITask, models: List[AIModel]) -> OrchestrationResult:
        """Execute task with iterative feedback loop."""
        start_time = time.time()
        max_iterations = 3
        total_cost = 0.0
        all_responses = []

        current_prompt = task.prompt

        for iteration in range(max_iterations):
            iteration_responses = []

            # Get responses from all models
            for model in models:
                try:
                    response = await self._call_model_api(model, current_prompt, task.max_tokens, task.temperature)
                    iteration_responses.append(response)
                    total_cost += self._calculate_cost(model, response)
                except Exception as e:
                    self.logger.warning(f"Model {model.value} iteration {iteration} failed: {e}")

            all_responses.extend(iteration_responses)

            if iteration < max_iterations - 1:
                # Create feedback prompt for next iteration
                feedback = self._generate_feedback_prompt(iteration_responses)
                current_prompt = f"{task.prompt}\n\nFeedback from previous iteration:\n{feedback}\n\nPlease improve your analysis:"

        total_time = time.time() - start_time

        # Use best response as final answer
        final_answer = self._select_best_response(iteration_responses)

        result = OrchestrationResult(
            task_id=task.id,
            execution_mode=ExecutionMode.FEEDBACK_LOOP,
            models_used=[m.value for m in models],
            total_cost=total_cost,
            total_time=total_time,
            quality_score=self._evaluate_response_quality({'content': final_answer}),
            responses=all_responses,
            final_answer=final_answer,
            metadata={'iterations': max_iterations, 'total_responses': len(all_responses)}
        )

        return result

    async def _call_model_api(self, model: AIModel, prompt: str, max_tokens: int = 4000,
                             temperature: float = 0.7) -> Dict[str, Any]:
        """
        Call the API for a specific model.

        In production, this would integrate with actual API providers.
        """
        caps = self.model_selector.model_capabilities[model]

        # Update rate limiting
        caps.current_requests += 1
        caps.last_request_time = datetime.now(UTC)

        # Simulate API call (replace with actual implementation)
        await asyncio.sleep(0.1)  # Simulate network latency

        # Mock response based on model capabilities
        response_length = int(max_tokens * (0.7 + np.random.random() * 0.3))
        quality_factor = caps.quality_score * (0.8 + np.random.random() * 0.4)

        mock_content = f"Response from {model.value} (quality: {quality_factor:.2f}): {prompt[:100]}..."
        mock_content += f"\n\nDetailed analysis would go here with {response_length} tokens of high-quality content."

        response = {
            'model': model.value,
            'content': mock_content,
            'tokens_used': response_length,
            'finish_reason': 'stop',
            'quality_score': quality_factor
        }

        # Update performance tracking
        response_time = 0.1 + np.random.random() * 2.0  # 0.1-2.1 seconds
        self.model_selector.performance_history[model].append(quality_factor)

        return response

    def _detect_complexity(self, prompt: str) -> TaskComplexity:
        """Auto-detect task complexity from prompt."""
        prompt_lower = prompt.lower()

        # Count complexity indicators
        complexity_indicators = {
            TaskComplexity.ENTERPRISE: ['architect', 'system', 'enterprise', 'strategy', 'design', 'multiple'],
            TaskComplexity.COMPLEX: ['complex', 'advanced', 'optimize', 'refactor', 'integrate'],
            TaskComplexity.MODERATE: ['implement', 'create', 'build', 'analyze', 'review'],
            TaskComplexity.SIMPLE: ['fix', 'update', 'change', 'add', 'remove'],
            TaskComplexity.TRIVIAL: ['what', 'how', 'explain', 'simple']
        }

        scores = {}
        for complexity, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in prompt_lower)
            scores[complexity] = score

        # Return highest scoring complexity
        return max(scores, key=scores.get)

    def _calculate_cost(self, model: AIModel, response: Dict[str, Any]) -> float:
        """Calculate cost for a model response."""
        caps = self.model_selector.model_capabilities[model]
        tokens_used = response.get('tokens_used', 0)
        return tokens_used * caps.cost_per_token + caps.cost_per_request

    def _evaluate_response_quality(self, response: Dict[str, Any]) -> float:
        """Evaluate response quality (placeholder implementation)."""
        if not response:
            return 0.0

        content = response.get('content', '')
        quality_score = response.get('quality_score', 0.5)

        # Simple heuristics
        if len(content) > 1000:
            quality_score += 0.1
        if 'analysis' in content.lower():
            quality_score += 0.1
        if 'code' in content.lower() or '```' in content:
            quality_score += 0.1

        return min(quality_score, 1.0)

    def _aggregate_responses(self, responses: List[Dict[str, Any]]) -> str:
        """Aggregate multiple responses into final answer."""
        if not responses:
            return ""

        if len(responses) == 1:
            return responses[0].get('content', '')

        # Simple aggregation - take best response
        scored_responses = [(self._evaluate_response_quality(r), r) for r in responses]
        best_response = max(scored_responses, key=lambda x: x[0])[1]

        return best_response.get('content', '')

    def _generate_feedback_prompt(self, responses: List[Dict[str, Any]]) -> str:
        """Generate feedback prompt for next iteration."""
        if not responses:
            return "Please provide a more detailed analysis."

        strengths = []
        weaknesses = []

        for response in responses:
            content = response.get('content', '')
            if len(content) > 500:
                strengths.append("Good detail")
            if 'code' in content:
                strengths.append("Includes code examples")

        feedback = "Strengths observed: " + ", ".join(strengths)
        feedback += "\nAreas for improvement: More specific recommendations, concrete examples"

        return feedback

    def _select_best_response(self, responses: List[Dict[str, Any]]) -> str:
        """Select the best response from multiple options."""
        if not responses:
            return ""

        scored = [(self._evaluate_response_quality(r), r) for r in responses]
        return max(scored, key=lambda x: x[0])[1].get('content', '')

    async def _init_api_clients(self) -> None:
        """Initialize API clients for different providers."""
        # Placeholder - would initialize actual API clients
        pass

    async def _update_performance_metrics(self, task: AITask, result: OrchestrationResult) -> None:
        """Update performance metrics after task completion."""
        # Track in history
        self.task_history.append({
            'task_id': task.id,
            'complexity': task.complexity.value,
            'execution_mode': result.execution_mode.value,
            'cost': result.total_cost,
            'time': result.total_time,
            'quality': result.quality_score,
            'models_used': result.models_used,
            'timestamp': datetime.now(UTC).isoformat()
        })

        # Update cost tracking
        for model_name in result.models_used:
            self.cost_tracking[model_name] += result.total_cost / len(result.models_used)

    async def _performance_monitoring_loop(self) -> None:
        """Continuous performance monitoring and optimization."""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes

                # Analyze performance trends
                if len(self.task_history) > 10:
                    recent_tasks = list(self.task_history)[-10:]

                    # Update model performance scores
                    for task_data in recent_tasks:
                        for model_name in task_data['models_used']:
                            # Find model enum from name
                            for model in AIModel:
                                if model.value == model_name:
                                    self.model_selector.performance_history[model].append(task_data['quality'])
                                    break

                # Log performance summary
                total_cost = sum(self.cost_tracking.values())
                total_tasks = len(self.task_history)

                if total_tasks > 0:
                    avg_cost = total_cost / total_tasks
                    avg_quality = statistics.mean([t['quality'] for t in self.task_history])

                    self.logger.info(f"Performance: {total_tasks} tasks, avg cost ${avg_cost:.4f}, avg quality {avg_quality:.2f}")

            except Exception as e:
                self.logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(60)

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        if not self.task_history:
            return {}

        tasks = list(self.task_history)

        return {
            'total_tasks': len(tasks),
            'total_cost': sum(self.cost_tracking.values()),
            'avg_cost_per_task': statistics.mean([t['cost'] for t in tasks]),
            'avg_quality_score': statistics.mean([t['quality'] for t in tasks]),
            'avg_execution_time': statistics.mean([t['time'] for t in tasks]),
            'model_usage': dict(self.cost_tracking),
            'complexity_distribution': {
                complexity: sum(1 for t in tasks if t['complexity'] == complexity.value)
                for complexity in TaskComplexity
            },
            'execution_mode_distribution': {
                mode: sum(1 for t in tasks if t['execution_mode'] == mode.value)
                for mode in ExecutionMode
            }
        }

    async def shutdown(self) -> None:
        """Clean shutdown of the orchestrator."""
        self.logger.info("Shutting down Multi-AI Orchestrator...")

        # Cancel active tasks
        for task in self.active_tasks.values():
            # In production, would cancel running API calls
            pass

        self.active_tasks.clear()

        # Shutdown executor
        self.executor.shutdown(wait=True)

        self.logger.info("Multi-AI Orchestrator shutdown complete")


# Global orchestrator instance
_multi_ai_orchestrator: Optional[MultiAIOrchestrator] = None

async def get_multi_ai_orchestrator() -> MultiAIOrchestrator:
    """Get or create global multi-AI orchestrator instance."""
    global _multi_ai_orchestrator
    if _multi_ai_orchestrator is None:
        _multi_ai_orchestrator = MultiAIOrchestrator()
        await _multi_ai_orchestrator.initialize()
    return _multi_ai_orchestrator
