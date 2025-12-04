"""
Real-Time Monitoring Dashboard - Elite System Observability

This module implements a comprehensive real-time monitoring system with:
- Prometheus metrics integration
- Grafana dashboard generation
- Custom performance metrics
- Real-time alerting
- System health visualization
- Performance analytics dashboard

Key Features:
- Live metrics collection and aggregation
- Custom metric definitions for all elite systems
- Alert manager integration
- Dashboard auto-generation
- Performance trend analysis
- System topology visualization
"""

import asyncio
import json
import time
import statistics
from datetime import datetime, UTC, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import aiofiles
from pathlib import Path
import psutil
import socket
import platform

try:
    import prometheus_client as prom
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("prometheus_client not available, using mock metrics")

@dataclass
class MetricDefinition:
    """Definition of a custom metric."""
    name: str
    description: str
    type: str  # gauge, counter, histogram
    labels: List[str] = field(default_factory=list)
    unit: str = ""

@dataclass
class SystemMetrics:
    """Real-time system metrics."""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # System resources
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_usage_percent: float = 0.0
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0

    # Elite system metrics
    active_agents: int = 0
    orchestrator_latency: float = 0.0
    hive_memory_compression: float = 0.0
    multi_ai_requests: int = 0
    fitness_score: float = 0.0
    deployments_active: int = 0

    # Performance indicators
    response_time_p50: float = 0.0
    response_time_p95: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0

@dataclass
class DashboardPanel:
    """Grafana dashboard panel definition."""
    title: str
    type: str  # graph, singlestat, table, heatmap
    targets: List[Dict[str, Any]] = field(default_factory=list)
    grid_pos: Dict[str, int] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AlertRule:
    """Prometheus alert rule definition."""
    name: str
    query: str
    duration: str
    severity: str
    description: str
    summary: str

class EliteMonitoringDashboard:
    """
    Elite Real-Time Monitoring Dashboard

    Comprehensive monitoring system providing:
    - Live metrics collection and visualization
    - Prometheus/Grafana integration
    - Custom elite system metrics
    - Automated dashboard generation
    - Real-time alerting and notifications
    - Performance analytics and insights
    """

    def __init__(self, prometheus_port: int = 8001, grafana_port: int = 3000):
        self.logger = logging.getLogger(__name__)

        self.prometheus_port = prometheus_port
        self.grafana_port = grafana_port

        # Metrics registry
        self.registry = prom.CollectorRegistry() if PROMETHEUS_AVAILABLE else None

        # Custom metrics
        self.custom_metrics: Dict[str, Any] = {}
        self._initialize_metrics()

        # Dashboard storage
        self.dashboards: Dict[str, Dict[str, Any]] = {}
        self.alert_rules: List[AlertRule] = []

        # Metrics buffer for analytics
        self.metrics_buffer: List[SystemMetrics] = []
        self.buffer_size = 1000

        # Collection intervals
        self.system_collection_interval = 5  # seconds
        self.elite_collection_interval = 10  # seconds

        # Background tasks
        self._collection_task: Optional[asyncio.Task] = None
        self._analytics_task: Optional[asyncio.Task] = None

        # System info
        self.hostname = socket.gethostname()
        self.system_info = self._get_system_info()

    def _initialize_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            self.logger.warning("Prometheus not available, using mock metrics")
            return

        # System resource metrics
        self.cpu_gauge = prom.Gauge(
            'ouroboros_cpu_percent',
            'CPU usage percentage',
            registry=self.registry
        )

        self.memory_gauge = prom.Gauge(
            'ouroboros_memory_percent',
            'Memory usage percentage',
            registry=self.registry
        )

        self.disk_gauge = prom.Gauge(
            'ouroboros_disk_usage_percent',
            'Disk usage percentage',
            registry=self.registry
        )

        # Elite system metrics
        self.active_agents_gauge = prom.Gauge(
            'ouroboros_active_agents',
            'Number of active agents',
            registry=self.registry
        )

        self.orchestrator_latency = prom.Histogram(
            'ouroboros_orchestrator_latency_seconds',
            'Orchestrator operation latency',
            registry=self.registry
        )

        self.hive_compression_gauge = prom.Gauge(
            'ouroboros_hive_compression_ratio',
            'Persistence hive compression ratio',
            registry=self.registry
        )

        self.multi_ai_requests = prom.Counter(
            'ouroboros_multi_ai_requests_total',
            'Total multi-AI requests',
            registry=self.registry
        )

        self.fitness_score_gauge = prom.Gauge(
            'ouroboros_fitness_score',
            'System fitness score (0-1)',
            registry=self.registry
        )

        self.response_time_histogram = prom.Histogram(
            'ouroboros_response_time_seconds',
            'Response time histogram',
            ['endpoint'],
            registry=self.registry
        )

        self.error_rate_gauge = prom.Gauge(
            'ouroboros_error_rate',
            'Error rate percentage',
            registry=self.registry
        )

        # Custom elite metrics
        self.deployment_counter = prom.Counter(
            'ouroboros_deployments_total',
            'Total deployments',
            ['status', 'environment'],
            registry=self.registry
        )

        self.ai_cost_gauge = prom.Gauge(
            'ouroboros_ai_cost_dollars',
            'Accumulated AI API costs',
            registry=self.registry
        )

    async def start_monitoring(self) -> None:
        """
        Start the real-time monitoring system.

        This initializes metrics collection, dashboard generation,
        and starts background monitoring tasks.
        """
        self.logger.info("Starting Elite Real-Time Monitoring Dashboard...")

        # Start Prometheus metrics server
        if PROMETHEUS_AVAILABLE:
            prom.start_http_server(port=self.prometheus_port, registry=self.registry)
            self.logger.info(f"Prometheus metrics server started on port {self.prometheus_port}")

        # Generate dashboards
        await self._generate_dashboards()

        # Generate alert rules
        await self._generate_alert_rules()

        # Start collection tasks
        self._collection_task = asyncio.create_task(self._metrics_collection_loop())
        self._analytics_task = asyncio.create_task(self._analytics_loop())

        self.logger.info("Elite Real-Time Monitoring Dashboard started successfully")

    async def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass

        if self._analytics_task:
            self._analytics_task.cancel()
            try:
                await self._analytics_task
            except asyncio.CancelledError:
                pass

        self.logger.info("Elite Real-Time Monitoring Dashboard stopped")

    async def record_metric(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """
        Record a custom metric value.

        Args:
            name: Metric name
            value: Metric value
            labels: Optional metric labels
        """
        if not PROMETHEUS_AVAILABLE:
            return

        # Update Prometheus metric
        if hasattr(self, f"{name}_gauge"):
            gauge = getattr(self, f"{name}_gauge")
            if labels:
                gauge.labels(**labels).set(value)
            else:
                gauge.set(value)

        elif hasattr(self, f"{name}_counter"):
            counter = getattr(self, f"{name}_counter")
            if labels:
                counter.labels(**labels).inc(value)
            else:
                counter.inc(value)

    async def get_current_metrics(self) -> SystemMetrics:
        """Get current system metrics snapshot."""
        metrics = SystemMetrics()

        # System resource metrics
        metrics.cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        metrics.memory_percent = memory.percent

        disk = psutil.disk_usage('/')
        metrics.disk_usage_percent = disk.percent

        network = psutil.net_io_counters()
        metrics.network_bytes_sent = network.bytes_sent
        metrics.network_bytes_recv = network.bytes_recv

        # Elite system metrics (would be populated by actual system calls)
        # For now, use mock values that would come from the actual systems
        metrics.active_agents = 5  # From orchestrator
        metrics.orchestrator_latency = 0.05  # seconds
        metrics.hive_memory_compression = 8.5  # compression ratio
        metrics.multi_ai_requests = 42  # total requests
        metrics.fitness_score = 0.75  # DEFCON score
        metrics.deployments_active = 1  # active deployments

        # Performance indicators
        metrics.response_time_p50 = 0.1  # seconds
        metrics.response_time_p95 = 0.5  # seconds
        metrics.error_rate = 0.02  # 2%
        metrics.throughput = 150  # requests/second

        return metrics

    async def get_metrics_history(self, hours: int = 1) -> List[SystemMetrics]:
        """Get historical metrics for analysis."""
        cutoff_time = datetime.now(UTC) - timedelta(hours=hours)

        return [
            m for m in self.metrics_buffer
            if m.timestamp > cutoff_time
        ]

    async def get_dashboard_json(self, dashboard_name: str) -> Optional[Dict[str, Any]]:
        """Get Grafana dashboard JSON definition."""
        return self.dashboards.get(dashboard_name)

    async def get_alert_status(self) -> Dict[str, Any]:
        """Get current alert status and active alerts."""
        # In production, this would query Prometheus Alertmanager
        return {
            "active_alerts": [],
            "silenced_alerts": [],
            "inhibited_alerts": []
        }

    async def export_metrics(self, format: str = "json") -> str:
        """
        Export metrics in specified format.

        Args:
            format: Export format (json, prometheus, csv)

        Returns:
            Formatted metrics data
        """
        if format == "json":
            metrics = await self.get_current_metrics()
            return json.dumps(asdict(metrics), indent=2, default=str)

        elif format == "prometheus":
            if PROMETHEUS_AVAILABLE:
                from prometheus_client import generate_latest
                return generate_latest(self.registry).decode('utf-8')
            else:
                return "# Prometheus not available"

        elif format == "csv":
            metrics = await self.get_current_metrics()
            lines = ["timestamp,metric,value"]
            for key, value in asdict(metrics).items():
                if isinstance(value, (int, float)):
                    lines.append(f"{metrics.timestamp.isoformat()},{key},{value}")
            return "\n".join(lines)

        return ""

    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop."""
        while True:
            try:
                # Collect system metrics
                metrics = await self.get_current_metrics()
                self.metrics_buffer.append(metrics)

                # Keep buffer size limited
                if len(self.metrics_buffer) > self.buffer_size:
                    self.metrics_buffer.pop(0)

                # Update Prometheus metrics
                if PROMETHEUS_AVAILABLE:
                    self.cpu_gauge.set(metrics.cpu_percent)
                    self.memory_gauge.set(metrics.memory_percent)
                    self.disk_gauge.set(metrics.disk_usage_percent)
                    self.active_agents_gauge.set(metrics.active_agents)
                    self.hive_compression_gauge.set(metrics.hive_memory_compression)
                    self.fitness_score_gauge.set(metrics.fitness_score)
                    self.error_rate_gauge.set(metrics.error_rate)

                await asyncio.sleep(self.system_collection_interval)

            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(5)

    async def _analytics_loop(self) -> None:
        """Background analytics and alerting loop."""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute

                # Perform analytics
                await self._perform_analytics()

                # Check alert conditions
                await self._check_alerts()

            except Exception as e:
                self.logger.error(f"Analytics loop error: {e}")
                await asyncio.sleep(10)

    async def _generate_dashboards(self) -> None:
        """Generate Grafana dashboards for elite system monitoring."""
        # System Overview Dashboard
        system_dashboard = {
            "dashboard": {
                "title": "Ouroboros Elite System Overview",
                "tags": ["ouroboros", "elite", "monitoring"],
                "timezone": "UTC",
                "panels": [
                    {
                        "title": "System Resources",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "ouroboros_cpu_percent",
                                "legendFormat": "CPU %"
                            },
                            {
                                "expr": "ouroboros_memory_percent",
                                "legendFormat": "Memory %"
                            },
                            {
                                "expr": "ouroboros_disk_usage_percent",
                                "legendFormat": "Disk %"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "title": "Elite System Fitness",
                        "type": "singlestat",
                        "targets": [
                            {
                                "expr": "ouroboros_fitness_score",
                                "legendFormat": "Fitness Score"
                            }
                        ],
                        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0}
                    },
                    {
                        "title": "Active Components",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "ouroboros_active_agents",
                                "legendFormat": "Active Agents"
                            },
                            {
                                "expr": "ouroboros_deployments_total",
                                "legendFormat": "Deployments"
                            }
                        ],
                        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "5s"
            }
        }

        # Performance Dashboard
        performance_dashboard = {
            "dashboard": {
                "title": "Ouroboros Performance Analytics",
                "tags": ["ouroboros", "performance", "analytics"],
                "timezone": "UTC",
                "panels": [
                    {
                        "title": "Response Time Distribution",
                        "type": "heatmap",
                        "targets": [
                            {
                                "expr": "rate(ouroboros_response_time_seconds_bucket[5m])",
                                "legendFormat": "Response Time"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 16, "x": 0, "y": 0}
                    },
                    {
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "ouroboros_error_rate",
                                "legendFormat": "Error Rate %"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 8, "x": 16, "y": 0}
                    }
                ],
                "time": {"from": "now-6h", "to": "now"},
                "refresh": "30s"
            }
        }

        self.dashboards["system_overview"] = system_dashboard
        self.dashboards["performance_analytics"] = performance_dashboard

        # Save dashboards to files
        dashboards_dir = Path("dashboards")
        dashboards_dir.mkdir(exist_ok=True)

        for name, dashboard in self.dashboards.items():
            dashboard_path = dashboards_dir / f"{name}.json"
            async with aiofiles.open(dashboard_path, 'w') as f:
                await f.write(json.dumps(dashboard, indent=2))

    async def _generate_alert_rules(self) -> None:
        """Generate Prometheus alert rules."""
        self.alert_rules = [
            AlertRule(
                name="HighCPUUsage",
                query="ouroboros_cpu_percent > 90",
                duration="5m",
                severity="warning",
                description="CPU usage is above 90%",
                summary="High CPU usage detected"
            ),
            AlertRule(
                name="HighMemoryUsage",
                query="ouroboros_memory_percent > 85",
                duration="5m",
                severity="warning",
                description="Memory usage is above 85%",
                summary="High memory usage detected"
            ),
            AlertRule(
                name="LowFitnessScore",
                query="ouroboros_fitness_score < 0.5",
                duration="10m",
                severity="critical",
                description="System fitness score is critically low",
                summary="Critical system health issue"
            ),
            AlertRule(
                name="HighErrorRate",
                query="ouroboros_error_rate > 0.05",
                duration="5m",
                severity="warning",
                description="Error rate is above 5%",
                summary="High error rate detected"
            )
        ]

        # Save alert rules
        rules_dir = Path("monitoring") / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        rules_config = {
            "groups": [
                {
                    "name": "ouroboros_alerts",
                    "rules": [
                        {
                            "alert": rule.name,
                            "expr": rule.query,
                            "for": rule.duration,
                            "labels": {"severity": rule.severity},
                            "annotations": {
                                "description": rule.description,
                                "summary": rule.summary
                            }
                        } for rule in self.alert_rules
                    ]
                }
            ]
        }

        rules_path = rules_dir / "ouroboros_alerts.yml"
        async with aiofiles.open(rules_path, 'w') as f:
            import yaml
            yaml_content = yaml.dump(rules_config, default_flow_style=False)
            await f.write(yaml_content)

    async def _perform_analytics(self) -> None:
        """Perform real-time analytics on collected metrics."""
        if len(self.metrics_buffer) < 10:
            return

        recent_metrics = self.metrics_buffer[-10:]

        # Calculate trends
        cpu_trend = self._calculate_trend([m.cpu_percent for m in recent_metrics])
        memory_trend = self._calculate_trend([m.memory_percent for m in recent_metrics])
        fitness_trend = self._calculate_trend([m.fitness_score for m in recent_metrics])

        # Log significant changes
        if cpu_trend and abs(cpu_trend[-1]) > 10:
            self.logger.warning(f"CPU usage trend changed significantly: {cpu_trend[-1]:.2f}%")

        if fitness_trend and fitness_trend[-1] < -0.05:
            self.logger.warning(f"System fitness declining: {fitness_trend[-1]:.3f} per measurement")

    async def _check_alerts(self) -> None:
        """Check for alert conditions."""
        if not self.metrics_buffer:
            return

        latest = self.metrics_buffer[-1]

        alerts = []

        if latest.cpu_percent > 90:
            alerts.append("High CPU usage")

        if latest.memory_percent > 85:
            alerts.append("High memory usage")

        if latest.fitness_score < 0.5:
            alerts.append("Low fitness score")

        if latest.error_rate > 0.05:
            alerts.append("High error rate")

        if alerts:
            self.logger.warning(f"Active alerts: {', '.join(alerts)}")

    def _calculate_trend(self, values: List[float]) -> Optional[List[float]]:
        """Calculate linear trend for values."""
        if len(values) < 2:
            return None

        n = len(values)
        x = list(range(n))
        y = values

        # Linear regression
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_xx = sum(xi * xi for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)

        return [slope * xi for xi in x]

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            "hostname": self.hostname,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "total_disk_gb": round(psutil.disk_usage('/').total / (1024**3), 2)
        }

    async def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            "system_info": self.system_info,
            "monitoring_status": {
                "prometheus_available": PROMETHEUS_AVAILABLE,
                "prometheus_port": self.prometheus_port,
                "metrics_buffer_size": len(self.metrics_buffer),
                "active_dashboards": len(self.dashboards),
                "alert_rules_count": len(self.alert_rules)
            },
            "current_metrics": asdict(await self.get_current_metrics()) if self.metrics_buffer else None
        }


# Global monitoring dashboard instance
_monitoring_dashboard: Optional[EliteMonitoringDashboard] = None

async def get_monitoring_dashboard() -> EliteMonitoringDashboard:
    """Get or create global monitoring dashboard instance."""
    global _monitoring_dashboard
    if _monitoring_dashboard is None:
        _monitoring_dashboard = EliteMonitoringDashboard()
        await _monitoring_dashboard.start_monitoring()
    return _monitoring_dashboard
