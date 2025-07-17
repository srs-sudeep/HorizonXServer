"""Database session management."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.core.config import settings

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,  # SQL logging
    future=True,  # Enable future SQLAlchemy features
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=20,  # Maximum number of connections in the pool
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,  # Timeout for getting connection from pool
    pool_recycle=1800,  # Recycle connections after 30 minutes
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Don't expire objects after commit
    autoflush=False,  # Don't auto flush changes
    autocommit=False,  # Don't auto commit transactions
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session.

    Yields:
        AsyncSession: Database session

    Example:
        async def my_endpoint(db: AsyncSession = Depends(get_db)):
            query = select(User).where(User.id == 1)
            result = await db.execute(query)
            user = result.scalar_one_or_none()
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# For testing: create engine without connection pooling
def create_test_engine():
    """Create test engine without connection pooling."""

    return create_async_engine(
        str(settings.DATABASE_URL),
        echo=settings.DEBUG,
        future=True,
        poolclass=NullPool,  # Disable connection pooling for tests
    )