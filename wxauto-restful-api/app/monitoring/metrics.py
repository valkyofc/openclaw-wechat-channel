"""
Metrics Collection Module

Collects and aggregates metrics for the wxauto API, including:
- Request queue metrics
- Operation execution times
- Concurrency statistics
- Error rates
"""
import time
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and aggregates metrics for the API

    Tracks:
    - Queue length over time
    - Request processing times
    - Success/failure rates
    - Concurrency conflicts
    """

    def __init__(self, retention_seconds: int = 3600):
        """
        Initialize the metrics collector

        Args:
            retention_seconds: How long to keep metrics data (default: 1 hour)
        """
        self._retention_seconds = retention_seconds

        # Metrics storage
        self._request_times: List[Dict] = []  # Request processing times
        self._queue_lengths: List[Dict] = []  # Queue length snapshots
        self._errors: List[Dict] = []          # Error events
        self._concurrency_events: List[Dict] = []  # Concurrency conflicts

        # Aggregated counters
        self._counters = defaultdict(int)

        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

        # Start cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start the metrics collector and cleanup task"""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("MetricsCollector started")

    async def stop(self) -> None:
        """Stop the metrics collector"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("MetricsCollector stopped")

    async def record_request(
        self,
        operation: str,
        duration: float,
        success: bool,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Record a request metric

        Args:
            operation: The operation name
            duration: Processing time in seconds
            success: Whether the operation succeeded
            metadata: Optional additional metadata
        """
        async with self._lock:
            self._request_times.append({
                'operation': operation,
                'duration': duration,
                'success': success,
                'timestamp': datetime.now(),
                'metadata': metadata or {}
            })
            self._counters[f'requests_{operation}'] += 1
            if success:
                self._counters['requests_success'] += 1
            else:
                self._counters['requests_error'] += 1

    async def record_queue_length(self, length: int) -> None:
        """
        Record a queue length snapshot

        Args:
            length: Current queue length
        """
        async with self._lock:
            self._queue_lengths.append({
                'length': length,
                'timestamp': datetime.now()
            })

    async def record_error(
        self,
        operation: str,
        error_type: str,
        message: str
    ) -> None:
        """
        Record an error event

        Args:
            operation: The operation that failed
            error_type: Type of error
            message: Error message
        """
        async with self._lock:
            self._errors.append({
                'operation': operation,
                'error_type': error_type,
                'message': message,
                'timestamp': datetime.now()
            })
            self._counters['errors_total'] += 1
            self._counters[f'errors_{error_type}'] += 1

    async def record_concurrency_event(self, event_type: str) -> None:
        """
        Record a concurrency-related event

        Args:
            event_type: Type of event (e.g., 'lock_acquired', 'lock_released')
        """
        async with self._lock:
            self._concurrency_events.append({
                'event_type': event_type,
                'timestamp': datetime.now()
            })
            self._counters[f'concurrency_{event_type}'] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics summary

        Returns:
            Dictionary containing metrics summary
        """
        # Calculate percentiles for request times
        durations = [r['duration'] for r in self._request_times if r['success']]
        percentile_50 = self._percentile(durations, 50) if durations else 0
        percentile_95 = self._percentile(durations, 95) if durations else 0
        percentile_99 = self._percentile(durations, 99) if durations else 0

        # Calculate success rate
        total_requests = self._counters['requests_success'] + self._counters['requests_error']
        success_rate = (
            self._counters['requests_success'] / total_requests
            if total_requests > 0
            else 0
        )

        # Average queue length
        avg_queue_length = (
            sum(q['length'] for q in self._queue_lengths) / len(self._queue_lengths)
            if self._queue_lengths
            else 0
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'requests': {
                'total': total_requests,
                'success': self._counters['requests_success'],
                'errors': self._counters['requests_error'],
                'success_rate': success_rate,
                'duration_percentiles': {
                    'p50': percentile_50,
                    'p95': percentile_95,
                    'p99': percentile_99
                }
            },
            'queue': {
                'current_length': self._queue_lengths[-1]['length'] if self._queue_lengths else 0,
                'average_length': avg_queue_length,
                'max_length': max((q['length'] for q in self._queue_lengths), default=0)
            },
            'errors': {
                'total': self._counters['errors_total'],
                'recent_errors': [
                    {
                        'operation': e['operation'],
                        'type': e['error_type'],
                        'message': e['message'],
                        'timestamp': e['timestamp'].isoformat()
                    }
                    for e in self._errors[-10:]  # Last 10 errors
                ]
            },
            'counters': dict(self._counters)
        }

    def get_operation_metrics(self, operation: str) -> Dict[str, Any]:
        """
        Get metrics for a specific operation

        Args:
            operation: The operation name

        Returns:
            Dictionary containing operation-specific metrics
        """
        operation_requests = [r for r in self._request_times if r['operation'] == operation]

        if not operation_requests:
            return {
                'operation': operation,
                'total_requests': 0,
                'success_rate': 0,
                'avg_duration': 0
            }

        successful = [r for r in operation_requests if r['success']]
        durations = [r['duration'] for r in successful]

        return {
            'operation': operation,
            'total_requests': len(operation_requests),
            'successful_requests': len(successful),
            'failed_requests': len(operation_requests) - len(successful),
            'success_rate': len(successful) / len(operation_requests),
            'avg_duration': sum(durations) / len(durations) if durations else 0,
            'min_duration': min(durations) if durations else 0,
            'max_duration': max(durations) if durations else 0
        }

    async def reset_metrics(self) -> None:
        """Reset all metrics"""
        async with self._lock:
            self._request_times.clear()
            self._queue_lengths.clear()
            self._errors.clear()
            self._concurrency_events.clear()
            self._counters.clear()
            logger.info("Metrics reset")

    async def _cleanup_loop(self) -> None:
        """Periodically cleanup old metrics"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                await self._cleanup_old_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than retention period"""
        cutoff_time = datetime.now() - timedelta(seconds=self._retention_seconds)

        async with self._lock:
            # Cleanup old request times
            self._request_times = [
                r for r in self._request_times
                if r['timestamp'] > cutoff_time
            ]

            # Cleanup old queue lengths
            self._queue_lengths = [
                q for q in self._queue_lengths
                if q['timestamp'] > cutoff_time
            ]

            # Cleanup old errors
            self._errors = [
                e for e in self._errors
                if e['timestamp'] > cutoff_time
            ]

            # Cleanup old concurrency events
            self._concurrency_events = [
                c for c in self._concurrency_events
                if c['timestamp'] > cutoff_time
            ]

            logger.debug(f"Cleaned up metrics older than {cutoff_time}")

    @staticmethod
    def _percentile(data: List[float], p: int) -> float:
        """
        Calculate percentile of a list of numbers

        Args:
            data: List of numbers
            p: Percentile to calculate (0-100)

        Returns:
            The percentile value
        """
        if not data:
            return 0

        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * (p / 100)
        f = int(k)
        c = k - f

        if f + 1 < len(sorted_data):
            return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
        else:
            return sorted_data[f]
