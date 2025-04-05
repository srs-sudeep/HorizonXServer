"""API dependencies."""
from typing import Generator, List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.permission import Permission
from src.app.models.user import User
from src.app.schemas.auth import TokenPayload
from src.app.services.user import UserService
from src.core.config import settings
from src.core.db.session import get_db

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user from token.

    Args:
        token: JWT token
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Create exception
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)

        # Check token type
        if token_data.type != "access":
            raise credentials_exception

        # Check if token is expired
        if token_data.exp is None:
            raise credentials_exception

        # Get user ID from token
        user_id: Optional[int] = (
            int(token_data.sub) if token_data.sub else None
        )
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user

    Returns:
        Current active user

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current superuser.

    Args:
        current_user: Current user

    Returns:
        Current superuser

    Raises:
        HTTPException: If user is not superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def has_permission(resource: str, action: str):
    """
    Check if user has permission.

    Args:
        resource: Resource name
        action: Action name

    Returns:
        Dependency function
    """

    async def check_permission(
        current_user: User = Depends(get_current_user),
    ) -> User:
        """
        Check if user has permission.

        Args:
            current_user: Current user

        Returns:
            Current user

        Raises:
            HTTPException: If user does not have permission
        """
        # Superuser has all permissions
        if current_user.is_superuser:
            return current_user

        # Check if user has permission
        for role in current_user.roles:
            for permission in role.permissions:
                if (
                    permission.resource == resource
                    and permission.action == action
                ):
                    return current_user

        # User does not have permission
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return check_permission
