"""User service."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.models.user import User
from src.app.schemas.user import UserCreate
from src.core.security import get_password_hash, verify_password
from .base import BaseService


class UserService(BaseService[User]):
    """User service."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        super().__init__(db, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        query = (
            select(User).where(User.email == email).options(selectinload(User.roles))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        query = (
            select(User)
            .where(User.username == username)
            .options(selectinload(User.roles))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, user_in: UserCreate) -> User:
        """Create new user."""
        user = await self.create(
            email=user_in.email,
            username=user_in.username,
            hashed_password=get_password_hash(user_in.password),
        )
        return user

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = await self.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
