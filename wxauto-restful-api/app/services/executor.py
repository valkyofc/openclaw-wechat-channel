"""UI Operation Executor for WeChat Operations"""
import asyncio
import logging
import functools
from typing import Optional, Callable, Any, Dict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

logger = logging.getLogger(__name__)


class UIOperationExecutor:
    """
    Single-threaded executor for UI operations that need to run in isolation

    This ensures UI operations are serialized and don't block the main event loop.
    All operations run in a dedicated single thread to prevent concurrent access issues.
    """

    def __init__(self, max_workers: int = 1):
        """
        Initialize the executor

        Args:
            max_workers: Maximum number of worker threads (default: 1 for serial execution)
        """
        if max_workers != 1:
            logger.warning(
                f"UIOperationExecutor should use max_workers=1 for UI operations. "
                f"Got {max_workers}. This may cause concurrency issues."
            )

        self.max_workers = max_workers
        self._executor: Optional[ThreadPoolExecutor] = None
        self._running = False
        self._stats: Dict[str, int] = {
            "completed": 0,
            "failed": 0,
            "total": 0
        }

    def start(self) -> None:
        """Start the executor"""
        if not self._running:
            self._executor = ThreadPoolExecutor(
                max_workers=self.max_workers,
                thread_name_prefix="wx_ui_executor"
            )
            self._running = True
            logger.info(f"UIOperationExecutor started with {self.max_workers} worker(s)")

    def stop(self) -> None:
        """
        Stop the executor and cleanup resources

        Waits for all pending operations to complete before shutting down.
        """
        if self._running and self._executor:
            logger.info("Stopping UIOperationExecutor...")
            self._executor.shutdown(wait=True)
            self._running = False
            logger.info("UIOperationExecutor stopped")

    async def execute(
        self,
        func: Callable[..., Any],
        *args,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        """
        Execute a function in the executor with optional timeout

        Args:
            func: The function to execute
            *args: Positional arguments for the function
            timeout: Maximum time to wait for completion (None = no timeout)
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function execution

        Raises:
            asyncio.TimeoutError: If operation times out
            Exception: If operation fails
        """
        if not self._running:
            self.start()

        self._stats["total"] += 1

        # Wrap function with arguments
        func_wrapper = functools.partial(func, *args, **kwargs)

        loop = asyncio.get_event_loop()
        try:
            if timeout:
                # Execute with timeout
                result = await asyncio.wait_for(
                    loop.run_in_executor(self._executor, func_wrapper),
                    timeout=timeout
                )
            else:
                # Execute without timeout
                result = await loop.run_in_executor(self._executor, func_wrapper)

            self._stats["completed"] += 1
            logger.debug(f"Executor operation completed successfully")
            return result

        except asyncio.TimeoutError:
            self._stats["failed"] += 1
            logger.error(f"Executor operation timed out after {timeout}s")
            raise
        except Exception as e:
            self._stats["failed"] += 1
            logger.error(f"Error in executor: {e}", exc_info=True)
            raise

    def is_running(self) -> bool:
        """Check if the executor is running"""
        return self._running

    def get_stats(self) -> Dict[str, Any]:
        """
        Get executor statistics

        Returns:
            Dictionary containing executor statistics
        """
        return {
            **self._stats,
            "is_running": self._running,
            "max_workers": self.max_workers,
            "success_rate": (
                self._stats["completed"] / self._stats["total"]
                if self._stats["total"] > 0
                else 0.0
            )
        }

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

    def __del__(self):
        """Cleanup on deletion"""
        if self._running:
            self.stop()
