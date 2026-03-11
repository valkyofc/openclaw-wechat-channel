"""
Health Check Module

Provides health check endpoints for the wxauto API.
Monitors system health including queue status, executor status, and error rates.
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Performs health checks for the API and its components

    Checks:
    - Operation queue health
    - Executor status
    - Recent error rates
    - System responsiveness
    """

    def __init__(self):
        """Initialize the health checker"""
        self._last_check_time: Optional[datetime] = None
        self._health_history: List[Dict] = []
        self._max_history = 100

    async def check_health(
        self,
        queue_stats: Optional[Dict] = None,
        executor_stats: Optional[Dict] = None,
        metrics_collector=None
    ) -> Dict[str, Any]:
        """
        Perform a comprehensive health check

        Args:
            queue_stats: Optional statistics from the operation queue
            executor_stats: Optional statistics from the executor
            metrics_collector: Optional metrics collector instance

        Returns:
            Dictionary containing health status
        """
        start_time = datetime.now()
        health_status = {
            'status': 'healthy',
            'timestamp': start_time.isoformat(),
            'checks': {}
        }

        # Check queue health
        if queue_stats:
            queue_health = self._check_queue_health(queue_stats)
            health_status['checks']['queue'] = queue_health
            if queue_health['status'] != 'healthy':
                health_status['status'] = 'degraded'

        # Check executor health
        if executor_stats:
            executor_health = self._check_executor_health(executor_stats)
            health_status['checks']['executor'] = executor_health
            if executor_health['status'] != 'healthy':
                health_status['status'] = 'degraded'

        # Check metrics if available
        if metrics_collector:
            metrics_health = await self._check_metrics_health(metrics_collector)
            health_status['checks']['metrics'] = metrics_health
            if metrics_health['status'] == 'unhealthy':
                health_status['status'] = 'unhealthy'

        # Calculate check duration
        duration = (datetime.now() - start_time).total_seconds()
        health_status['duration_ms'] = duration * 1000

        # Store in history
        self._health_history.append(health_status)
        if len(self._health_history) > self._max_history:
            self._health_history.pop(0)

        self._last_check_time = datetime.now()

        return health_status

    def _check_queue_health(self, stats: Dict) -> Dict[str, Any]:
        """
        Check queue health

        Args:
            stats: Queue statistics

        Returns:
            Dictionary with queue health status
        """
        status = 'healthy'
        issues = []

        # Check if queue is running
        if not stats.get('is_running', False):
            status = 'unhealthy'
            issues.append('Queue is not running')

        # Check queue length
        queue_length = stats.get('queue_length', 0)
        if queue_length > 50:
            status = 'degraded'
            issues.append(f'Queue length is high: {queue_length}')

        # Check failure rate
        total = stats.get('total', 0)
        failed = stats.get('failed', 0)
        if total > 0:
            failure_rate = failed / total
            if failure_rate > 0.1:  # More than 10% failures
                status = 'unhealthy'
                issues.append(f'High failure rate: {failure_rate:.1%}')

        return {
            'status': status,
            'issues': issues,
            'stats': {
                'is_running': stats.get('is_running', False),
                'queue_length': queue_length,
                'total_requests': total,
                'failed_requests': failed
            }
        }

    def _check_executor_health(self, stats: Dict) -> Dict[str, Any]:
        """
        Check executor health

        Args:
            stats: Executor statistics

        Returns:
            Dictionary with executor health status
        """
        status = 'healthy'
        issues = []

        # Check if executor is running
        if not stats.get('is_running', False):
            status = 'unhealthy'
            issues.append('Executor is not running')

        # Check success rate
        success_rate = stats.get('success_rate', 1.0)
        if success_rate < 0.9:  # Less than 90% success
            status = 'degraded'
            issues.append(f'Low success rate: {success_rate:.1%}')

        if success_rate < 0.7:  # Less than 70% success
            status = 'unhealthy'
            issues.append(f'Very low success rate: {success_rate:.1%}')

        return {
            'status': status,
            'issues': issues,
            'stats': {
                'is_running': stats.get('is_running', False),
                'success_rate': success_rate,
                'total_operations': stats.get('total', 0),
                'completed': stats.get('completed', 0),
                'failed': stats.get('failed', 0)
            }
        }

    async def _check_metrics_health(self, metrics_collector) -> Dict[str, Any]:
        """
        Check metrics collector health

        Args:
            metrics_collector: Metrics collector instance

        Returns:
            Dictionary with metrics health status
        """
        status = 'healthy'
        issues = []

        # Get metrics
        metrics = metrics_collector.get_metrics()

        # Check error rate
        error_rate = 1 - metrics['requests']['success_rate']
        if error_rate > 0.05:  # More than 5% errors
            status = 'degraded'
            issues.append(f'High error rate: {error_rate:.1%}')

        if error_rate > 0.15:  # More than 15% errors
            status = 'unhealthy'
            issues.append(f'Very high error rate: {error_rate:.1%}')

        # Check for recent errors
        recent_errors = len(metrics['errors']['recent_errors'])
        if recent_errors > 20:
            status = 'degraded'
            issues.append(f'Many recent errors: {recent_errors}')

        return {
            'status': status,
            'issues': issues,
            'stats': {
                'error_rate': error_rate,
                'recent_errors': recent_errors,
                'avg_duration_p95': metrics['requests']['duration_percentiles']['p95']
            }
        }

    def get_health_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent health check results

        Args:
            limit: Maximum number of results to return

        Returns:
            List of recent health check results
        """
        return self._health_history[-limit:]

    def get_uptime(self) -> Optional[float]:
        """
        Get uptime since last health check

        Returns:
            Uptime in seconds, or None if no checks performed
        """
        if not self._last_check_time:
            return None

        return (datetime.now() - self._last_check_time).total_seconds()

    async def readiness_probe(self) -> bool:
        """
        Simple readiness check

        Returns:
            True if the system is ready to handle requests
        """
        # In a real implementation, check:
        # - Queue is initialized
        # - Executor is running
        # - Dependencies are available
        return True

    async def liveness_probe(self) -> bool:
        """
        Simple liveness check

        Returns:
            True if the system is alive
        """
        # In a real implementation, check:
        # - Event loop is running
        # - No deadlocks
        # - Responsive to requests
        return True
