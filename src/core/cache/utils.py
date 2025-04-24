"""Cache utilities."""
from typing import Any, Callable, Optional, Union

from fastapi import Depends
from fastapi_cache.decorator import cache

from src.app.api.deps import get_current_user
from src.app.models.user import User
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


def user_specific_cache_key(
    func,
    namespace: Optional[str] = "",
    user: User = Depends(get_current_user),
    **kwargs
):
    """
    Create cache key based on user.
    
    Args:
        func: The function being cached
        namespace: Optional cache namespace
        user: Current user from dependency
        kwargs: Additional arguments
        
    Returns:
        Cache key string including username
    """
    return f"{namespace}:{func.__name__}:user:{user.username}"

