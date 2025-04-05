"""Cache utilities."""
from typing import Any, Callable, Optional, Union

from fastapi_cache.decorator import cache

from src.core.config import settings


def cached(
    expire: int = 60,
    namespace: Optional[str] = None,
    key_builder: Optional[Callable] = None,
) -> Any:
    """
    Cache decorator for API endpoints.

    Args:
        expire: Cache expiration time in seconds
        namespace: Cache namespace
        key_builder: Custom key builder function

    Returns:
        Decorated function
    """
    return cache(
        expire=expire,
        namespace=namespace,
        key_builder=key_builder,
    )
