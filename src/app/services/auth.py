"""Authentication service."""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.user import User
from src.app.schemas.auth import TokenPayload
from src.app.services.user import UserService
from src.core.config import settings
from src.core.db.session import get_db
from src.core.security import create_access_token, create_refresh_token


class AuthService:
    """Authentication service."""

    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        user_service: UserService = Depends(),
    ):
        """
        Initialize authentication service.

        Args:
            db: Database session
            user_service: User service
        """
        self.db = db
        self.user_service = user_service

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user.

        Args:
            username: Username
            password: Password

        Returns:
            User or None
        """
        return await self.user_service.authenticate(username, password)

    def create_tokens(self, user_id: int) -> dict:
        """
        Create access and refresh tokens.

        Args:
            user_id: User ID

        Returns:
            Dictionary with tokens
        """
        return {
            "access_token": create_access_token(user_id),
            "refresh_token": create_refresh_token(user_id),
            "token_type": "bearer",
        }

    async def refresh_tokens(self, refresh_token: str) -> dict:
        """
        Refresh tokens.

        Args:
            refresh_token: Refresh token

        Returns:
            Dictionary with new tokens

        Raises:
            HTTPException: If refresh token is invalid
        """
        try:
            # Decode refresh token
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            token_data = TokenPayload(**payload)

            # Check token type
            if token_data.type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type",
                )

            # Check if token is expired
            if token_data.exp < datetime.utcnow().timestamp():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                )

            # Get user
            user = await self.user_service.get_by_id(int(token_data.sub))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            # Create new tokens
            return self.create_tokens(user.id)

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
