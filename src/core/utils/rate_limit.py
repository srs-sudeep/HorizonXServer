"""Rate limiting utilities."""

import time
from typing import Callable, Dict, Optional, Tuple

from fastapi import Depends, HTTPException, Request, status
from redis import asyncio as aioredis

from src.core.config import settings


class RateLimiter:
    """Rate limiter using Redis."""

    def __init__(
        self,
        redis_client: aioredis.Redis,
        times: int = 100,
        seconds: int = 60,
    ):
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client
            times: Number of requests allowed
            seconds: Time window in seconds
        """
        self.redis_client = redis_client
        self.times = times
        self.seconds = seconds

    async def is_rate_limited(self, key: str) -> Tuple[bool, Dict]:
        """
        Check if request is rate limited.

        Args:
            key: Rate limit key

        Returns:
            Tuple of (is_limited, rate_limit_info)
        """
        # Get current timestamp
        current = int(time.time())
        time_window = current - self.seconds

        # Create pipeline
        async with self.redis_client.pipeline() as pipe:
            # Remove old requests
            await pipe.zremrangebyscore(key, 0, time_window)
            # Add current request
            await pipe.zadd(key, {str(current): current})
            # Get count of requests in window
            await pipe.zcount(key, time_window, "+inf")
            # Set key expiration
            await pipe.expire(key, self.seconds)
            # Execute pipeline
            _, _, count, _ = await pipe.execute()

        # Check if rate limited
        is_limited = count > self.times

        # Return rate limit info
        rate_limit_info = {
            "limit": self.times,
            "remaining": max(0, self.times - count),
            "reset": self.seconds - (current % self.seconds),
        }

        return is_limited, rate_limit_info


def create_rate_limiter(
    times: Optional[int] = None,
    seconds: Optional[int] = None,
) -> Callable:
    """
    Create rate limiter dependency.

    Args:
        times: Number of requests allowed
        seconds: Time window in seconds

    Returns:
        Rate limiter dependency
    """
    # Parse default rate limit
    if times is None or seconds is None:
        default_rate_limit = settings.RATE_LIMIT_DEFAULT
        try:
            default_times, default_period = default_rate_limit.split("/")
            default_times = int(default_times)
            if default_period.lower() == "second":
                default_seconds = 1
            elif default_period.lower() == "minute":
                default_seconds = 60
            elif default_period.lower() == "hour":
                default_seconds = 3600
            elif default_period.lower() == "day":
                default_seconds = 86400
            else:
                default_seconds = 60
        except (ValueError, AttributeError):
            default_times = 100
            default_seconds = 60

        times = times or default_times
        seconds = seconds or default_seconds

    async def rate_limit(request: Request) -> None:
        """
        Rate limit requests.

        Args:
            request: FastAPI request

        Raises:
            HTTPException: If rate limited
        """
        if not settings.RATE_LIMIT_ENABLED:
            return

        # Get Redis client from app state
        redis_client = request.app.state.redis

        # Create rate limiter
        limiter = RateLimiter(
            redis_client=redis_client,
            times=times,
            seconds=seconds,
        )

        # Get client IP
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0]
        else:
            client_ip = request.client.host  # type: ignore

        # Create rate limit key
        key = f"rate_limit:{client_ip}:{request.url.path}"

        # Check if rate limited
        is_limited, rate_limit_info = await limiter.is_rate_limited(key)

        # Set rate limit headers
        request.state.rate_limit_info = rate_limit_info

        # Raise exception if rate limited
        if is_limited:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
            )

    return rate_limit
