"""Redis cache client."""


from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from src.core.config import settings


async def init_redis_cache() -> None:
    """Initialize Redis cache."""
    redis = aioredis.from_url(
        str(settings.REDIS_URL),
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache:")
