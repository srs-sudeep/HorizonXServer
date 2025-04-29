"""Authentication service."""

from datetime import datetime
from typing import Optional, Dict

from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import User
from src.app.schemas import TokenPayload
from src.app.services.user import UserService
from src.core import create_access_token, create_refresh_token,settings


class AuthService:
    """Authentication service."""

    def __init__(self, db: AsyncSession):
        """Initialize authentication service."""
        self.db = db
        self.user_service = UserService(db)

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

    def create_tokens(self, username: str) -> Dict[str, str]:
        """
        Create access and refresh tokens.

        Args:
            username: Username of the user

        Returns:
            Dictionary with tokens
        """
        return {
            "access_token": create_access_token(username),
            "refresh_token": create_refresh_token(username),
            "token_type": "bearer",
        }

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, str]:
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
            if token_data.exp and token_data.exp < datetime.utcnow().timestamp():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                )

            # Get username from token
            if not token_data.sub:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )

            # Get user using username
            user = await self.user_service.get_by_username(token_data.sub)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            # Create new tokens
            return self.create_tokens(user.username)

        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
