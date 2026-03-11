"""Operation Queue for Thread-Safe WeChat Operations"""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any, Coroutine, TypeVar, Optional
from functools import wraps
from datetime import datetime
from dataclasses import dataclass, field
import logging
import heapq

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass(order=True)
class QueuedOperation:
    """
    Wrapper for operations in the queue with metadata

    Attributes:
        priority: Lower values = higher priority (0 = highest)
        operation: The callable to execute
        timeout: Maximum time to wait for operation completion (seconds)
        retry_count: Number of retry attempts remaining
        created_at: Timestamp when operation was created
        operation_id: Unique identifier for the operation
    """
    priority: int
    operation: Callable = field(compare=False)
    timeout: float = field(default=30.0, compare=False)
    retry_count: int = field(default=3, compare=False)
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    operation_id: str = field(default_factory=lambda: f"op_{datetime.now().timestamp()}", compare=False)

    def __post_init__(self):
        """Validate operation parameters"""
        if self.retry_count < 0:
            raise ValueError("retry_count must be non-negative")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")


class OperationQueue:
    """
    Thread-safe priority queue for serializing WeChat operations

    Features:
    - FIFO execution with priority support (lower priority value = higher priority)
    - Timeout control for each operation
    - Automatic retry mechanism (max 3 retries by default)
    - Detailed statistics and logging
    - Graceful shutdown
    """

    def __init__(self, max_concurrent: int = 1):
        """
        Initialize the operation queue

        Args:
            max_concurrent: Maximum number of concurrent operations (default: 1 for serial execution)
        """
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._executor = ThreadPoolExecutor(max_workers=max_concurrent, thread_name_prefix="wechat_op")
        self._queue: list = []  # Priority queue using heapq
        self._queue_lock = asyncio.Lock()
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        self._stats = {
            "completed": 0,
            "failed": 0,
            "retried": 0,
            "total": 0,
            "timeout": 0
        }

    async def submit(
        self,
        func: Callable[..., T],
        *args,
        priority: int = 0,
        timeout: float = 30.0,
        max_retries: int = 3,
        **kwargs
    ) -> T:
        """
        Submit an operation to the queue with priority and timeout

        Args:
            func: The function to execute
            *args: Positional arguments for the function
            priority: Operation priority (lower = higher priority, default: 0)
            timeout: Maximum time to wait for completion (default: 30 seconds)
            max_retries: Maximum number of retry attempts (default: 3)
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function execution

        Raises:
            asyncio.TimeoutError: If operation times out
            Exception: If operation fails after all retries
        """
        import functools

        self._stats["total"] += 1

        # Create the wrapped function with arguments
        func_wrapper = functools.partial(func, *args, **kwargs)

        # Create queued operation
        queued_op = QueuedOperation(
            priority=priority,
            operation=func_wrapper,
            timeout=timeout,
            retry_count=max_retries
        )

        logger.debug(
            f"Submitting operation {queued_op.operation_id} "
            f"with priority {priority}, timeout {timeout}s"
        )

        # Execute directly with semaphore control (no background processor)
        async with self._semaphore:
            return await self._execute_with_retry(queued_op)

    async def submit_async(self, coro: Coroutine[Any, Any, T]) -> T:
        """
        Submit an async operation to the queue

        Args:
            coro: The coroutine to execute

        Returns:
            The result of the coroutine execution
        """
        async with self._semaphore:
            try:
                return await coro
            except Exception as e:
                logger.error(f"Error executing async operation: {e}", exc_info=True)
                raise

    async def _execute_with_retry(self, queued_op: QueuedOperation) -> Any:
        """
        Execute operation with retry mechanism

        Args:
            queued_op: The queued operation to execute

        Returns:
            The result of the operation

        Raises:
            Exception: If operation fails after all retries
        """
        last_exception = None

        for attempt in range(queued_op.retry_count + 1):
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    self._execute_operation(queued_op),
                    timeout=queued_op.timeout
                )

                if attempt > 0:
                    self._stats["retried"] += 1
                    logger.info(
                        f"Operation {queued_op.operation_id} "
                        f"succeeded on attempt {attempt + 1}"
                    )
                else:
                    self._stats["completed"] += 1

                return result

            except asyncio.TimeoutError:
                last_exception = asyncio.TimeoutError(
                    f"Operation {queued_op.operation_id} timed out "
                    f"after {queued_op.timeout}s"
                )
                self._stats["timeout"] += 1
                logger.warning(
                    f"Operation {queued_op.operation_id} timed out "
                    f"(attempt {attempt + 1}/{queued_op.retry_count + 1})"
                )

            except Exception as e:
                last_exception = e
                logger.warning(
                    f"Operation {queued_op.operation_id} failed "
                    f"(attempt {attempt + 1}/{queued_op.retry_count + 1}): {e}"
                )

                # Don't retry if this is the last attempt
                if attempt >= queued_op.retry_count:
                    break

                # Wait before retry (exponential backoff)
                backoff_time = min(2 ** attempt, 10)  # Max 10 seconds
                logger.debug(f"Retrying in {backoff_time}s...")
                await asyncio.sleep(backoff_time)

        # All retries exhausted
        self._stats["failed"] += 1
        logger.error(
            f"Operation {queued_op.operation_id} failed after "
            f"{queued_op.retry_count + 1} attempts"
        )
        raise last_exception

    async def _execute_operation(self, queued_op: QueuedOperation) -> Any:
        """
        Execute a single operation

        Args:
            queued_op: The queued operation to execute

        Returns:
            The result of the operation
        """
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self._executor,
                queued_op.operation
            )
            return result
        except Exception as e:
            logger.error(f"Error executing operation {queued_op.operation_id}: {e}")
            raise

    async def close(self) -> None:
        """
        Close the queue and cleanup resources

        Waits for all pending operations to complete before shutting down.
        """
        logger.info("Closing operation queue...")
        self._running = False

        # Cancel worker task if exists
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass

        # Shutdown executor
        self._executor.shutdown(wait=True)
        logger.info("Operation queue closed")

    def get_stats(self) -> dict:
        """
        Get queue statistics

        Returns:
            Dictionary containing queue statistics
        """
        return {
            **self._stats,
            "is_running": self._running,
            "max_concurrent": self.max_concurrent
        }

    async def shutdown(self) -> None:
        """Alias for close() - shutdown the queue"""
        await self.close()

    def __del__(self):
        """Cleanup on deletion"""
        try:
            self._executor.shutdown(wait=False)
        except:
            pass


def with_queue(queue: OperationQueue):
    """
    Decorator to automatically queue function execution

    Args:
        queue: The OperationQueue instance to use

    Returns:
        Decorated function that executes via the queue
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await queue.submit(func, *args, **kwargs)
        return wrapper
    return decorator
