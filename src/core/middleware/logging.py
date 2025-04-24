"""Logging middleware."""

from typing import Callable

from fastapi import Request, Response
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.

        Args:
            request: FastAPI request
            call_next: Next middleware or endpoint

        Returns:
            Response
        """
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        response = await call_next(request)

        # Log response
        if response.status_code >= 400:
            # Log 4xx and 5xx responses as errors
            logger.error(
                f"Error {response.status_code}: {request.method} {request.url.path}"
            )
        else:
            # Log successful responses as info
            logger.info(
                f"Response: {response.status_code} for {request.method} {request.url.path}"
            )

        # Add rate limit headers if available
        if hasattr(request.state, "rate_limit_info"):
            rate_limit_info = request.state.rate_limit_info
            response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(
                rate_limit_info["remaining"]
            )
            response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset"])

        return response
