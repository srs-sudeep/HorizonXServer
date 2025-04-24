"""Application setup module."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from redis import asyncio as aioredis
from sqlalchemy import text

from src.app.api import api_router
from src.core.cache.client import init_redis_cache
from src.core.config import settings
from src.core.db.session import engine
from src.core.err import setup_exception_handlers
from src.core.log import setup_logging
from src.core.middleware import setup_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Setup logging
    setup_logging()

    try:
        # Test PostgreSQL connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Successfully connected to PostgreSQL")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        raise

    try:
        # Connect to Redis
        redis = aioredis.from_url(
            str(settings.REDIS_URL),
            encoding="utf8",
            decode_responses=True,
        )
        # Test Redis connection
        await redis.ping()
        logger.info("Successfully connected to Redis")
        app.state.redis = redis

        # Initialize Redis cache
        await init_redis_cache()
        logger.info("Redis cache initialized")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise

    # Yield control to FastAPI
    yield

    # Cleanup
    try:
        # Close Redis connection
        await redis.close()
        logger.info("Redis connection closed")

        # Close PostgreSQL connection pool
        await engine.dispose()
        logger.info("PostgreSQL connection pool closed")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")


def create_app() -> FastAPI:
    """
    Create FastAPI application.

    Returns:
        FastAPI application
    """
    # Create FastAPI application with docs only in development
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
        # Disable docs in production
        docs_url="/docs" if settings.APP_ENV == "development" else None,
        redoc_url="/redoc" if settings.APP_ENV == "development" else None,
        openapi_url="/openapi.json" if settings.APP_ENV == "development" else None,
    )

    # Setup middleware
    setup_middleware(app)

    # Setup exception handlers
    setup_exception_handlers(app)

    # Include API router
    app.include_router(api_router)

    # Root endpoint with environment-specific response
    @app.get("/")
    async def root():
        """Root endpoint."""
        response = {
            "message": "Welcome to FastAPI Boilerplate",
        }

        # Only include docs links in development
        if settings.APP_ENV == "development":
            response.update(
                {
                    "docs": "/docs",
                    "redoc": "/redoc",
                }
            )

        return response

    return app
