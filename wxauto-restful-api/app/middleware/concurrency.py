"""
Concurrency Control Middleware for WeChat Operations

This middleware ensures that all WeChat UI operations are executed serially
to prevent concurrent access issues. It integrates with the operation queue
system to provide thread-safe execution of WeChat automation operations.

Design Principles:
1. Identify WeChat operation paths that require serialization
2. Route these requests through the concurrency control mechanism
3. Allow non-WeChat paths to execute normally
4. Provide proper error handling and status codes
5. Log all concurrency control decisions for debugging
"""
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable, Set, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConcurrencyControlMiddleware(BaseHTTPMiddleware):
    """
    Middleware for controlling concurrent access to WeChat UI operations

    This middleware uses asyncio.Lock to ensure that only one WeChat operation
    executes at a time, preventing race conditions and UI state corruption.

    Paths requiring serialization:
        - /api/v1/wechat/*       - All WeChat operations
        - /api/v1/chat/*         - Chat operations (if enabled)
        - /api/v1/apps/*         - Application operations (if enabled)

    Paths excluded from serialization:
        - /api/v1/files/*        - File management (independent)
        - /api/v1/info/*         - Information queries (read-only)
        - /api/v1/listen/*       - WebSocket listeners (independent)
        - /docs, /openapi.json   - API documentation
        - /static/*              - Static files
        - /                      - Root endpoint

    Example:
        ```python
        from fastapi import FastAPI
        from app.middleware.concurrency import ConcurrencyControlMiddleware

        app = FastAPI()
        app.add_middleware(ConcurrencyControlMiddleware)
        ```
    """

    # Default paths that require serialization
    SERIALIZED_PATHS: Set[str] = {
        "/api/v1/wechat/",
        "/v1/wechat/",
        "/api/v1/chat/",
        "/v1/chat/",
        "/api/v1/apps/",
        "/v1/apps/",
    }

    # Paths explicitly excluded from serialization
    EXCLUDED_PATHS: Set[str] = {
        "/api/v1/files/",
        "/v1/files/",
        "/api/v1/info/",
        "/v1/info/",
        "/api/v1/listen/",
        "/v1/listen/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/static",
        "/",
    }

    def __init__(
        self,
        app,
        serialized_paths: Optional[Set[str]] = None,
        excluded_paths: Optional[Set[str]] = None,
        enable_logging: bool = True
    ):
        """
        Initialize the concurrency control middleware

        Args:
            app: The ASGI application
            serialized_paths: Custom set of paths requiring serialization
            excluded_paths: Custom set of paths to exclude from serialization
            enable_logging: Whether to log concurrency control decisions
        """
        super().__init__(app)

        # Use custom path sets if provided, otherwise use defaults
        self._serialized_paths = serialized_paths or self.SERIALIZED_PATHS
        self._excluded_paths = excluded_paths or self.EXCLUDED_PATHS

        # Lazy initialization of lock to ensure correct event loop
        self._lock: Optional[asyncio.Lock] = None

        # Configuration
        self._enable_logging = enable_logging

        # Statistics
        self._stats = {
            "total_requests": 0,
            "serialized_requests": 0,
            "non_serialized_requests": 0,
            "current_locked": False
        }

        logger.info(
            f"ConcurrencyControlMiddleware initialized. "
            f"Serialized paths: {len(self._serialized_paths)}, "
            f"Excluded paths: {len(self._excluded_paths)}"
        )

    def _needs_serialization(self, path: str) -> bool:
        """
        Check if a path needs serialization

        Args:
            path: The request path to check

        Returns:
            True if the path requires serialization, False otherwise
        """
        # Handle root path specially
        if path == '/':
            return False

        # Normalize the input path (remove trailing slash but keep root)
        normalized_path = path.rstrip('/') if path != '/' else path

        # First check if path is explicitly excluded
        for excluded in self._excluded_paths:
            # Skip empty normalized paths from root
            normalized_excluded = excluded.rstrip('/')
            if not normalized_excluded:
                continue

            # Check exact match or path starts with excluded path + '/'
            if normalized_path == normalized_excluded or normalized_path.startswith(normalized_excluded + '/'):
                return False

        # Then check if path requires serialization
        for serialized in self._serialized_paths:
            normalized_serialized = serialized.rstrip('/')
            if not normalized_serialized:
                continue

            # Check exact match or path starts with serialized path + '/'
            if normalized_path == normalized_serialized or normalized_path.startswith(normalized_serialized + '/'):
                return True

        # Default: no serialization for unknown paths
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Dispatch request with concurrency control

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler in the chain

        Returns:
            Response: The HTTP response

        Raises:
            HTTPException: If request processing fails
        """
        self._stats["total_requests"] += 1
        path = request.url.path

        try:
            # Check if this path requires serialization
            if self._needs_serialization(path):
                return await self._handle_serialized_request(request, call_next, path)
            else:
                return await self._handle_normal_request(request, call_next, path)

        except asyncio.TimeoutError as e:
            logger.error(f"Request timeout for {path}: {e}")
            self._stats["current_locked"] = False
            return JSONResponse(
                status_code=408,
                content={
                    "success": False,
                    "message": "Request timeout - operation took too long",
                    "detail": "The WeChat operation timed out. Please try again."
                }
            )

        except Exception as e:
            logger.error(f"Error processing request {path}: {e}", exc_info=True)
            self._stats["current_locked"] = False
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Internal server error",
                    "detail": str(e)
                }
            )

    async def _handle_serialized_request(
        self,
        request: Request,
        call_next: Callable,
        path: str
    ) -> Response:
        """
        Handle a request that requires serialization

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            path: The request path

        Returns:
            Response: The HTTP response
        """
        self._stats["serialized_requests"] += 1

        # Lazy initialization of lock
        if self._lock is None:
            self._lock = asyncio.Lock()
            logger.debug("Initialized asyncio.Lock for concurrency control")

        if self._enable_logging:
            logger.debug(f"Serializing request: {request.method} {path}")

        # Acquire lock to ensure serial execution
        self._stats["current_locked"] = True
        try:
            async with self._lock:
                response = await call_next(request)
                self._stats["current_locked"] = False
                return response

        finally:
            self._stats["current_locked"] = False

    async def _handle_normal_request(
        self,
        request: Request,
        call_next: Callable,
        path: str
    ) -> Response:
        """
        Handle a request that doesn't require serialization

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            path: The request path

        Returns:
            Response: The HTTP response
        """
        self._stats["non_serialized_requests"] += 1

        if self._enable_logging:
            logger.debug(f"Non-serialized request: {request.method} {path}")

        # Process normally without serialization
        response = await call_next(request)
        return response

    def get_stats(self) -> dict:
        """
        Get middleware statistics

        Returns:
            Dictionary containing middleware statistics
        """
        return {
            **self._stats,
            "lock_initialized": self._lock is not None,
            "serialized_path_count": len(self._serialized_paths),
            "excluded_path_count": len(self._excluded_paths)
        }

    def update_paths(
        self,
        serialized_paths: Optional[Set[str]] = None,
        excluded_paths: Optional[Set[str]] = None
    ) -> None:
        """
        Update the path configuration

        Args:
            serialized_paths: New set of paths requiring serialization
            excluded_paths: New set of paths to exclude from serialization
        """
        if serialized_paths is not None:
            self._serialized_paths = serialized_paths
            logger.info(f"Updated serialized paths: {len(serialized_paths)} paths")

        if excluded_paths is not None:
            self._excluded_paths = excluded_paths
            logger.info(f"Updated excluded paths: {len(excluded_paths)} paths")
