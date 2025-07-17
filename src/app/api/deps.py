"""API dependencies."""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.app.models import User, Role
from src.app.schemas import TokenPayload, UserResponse
from src.app.services import UserService
from src.core.config import settings
from src.core.db import get_db
from src.app.api.abac.evaluator import ABAuthorizer

# HTTP Bearer scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user from token.

    Args:
        credentials: Bearer token credentials
        db: Database session

    Returns:
        Current user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)

        # Check token type
        if token_data.type != "access":
            raise credentials_exception

        # Check if token is expired
        if token_data.exp is None:
            raise credentials_exception

        # Get id from token
        username: Optional[str] = token_data.sub
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Get user from database
    user_service = UserService(db)
    current_user = await user_service.get_by_username(username)
    if current_user is None:
        raise credentials_exception
    print(f"Current user: {current_user} with ID: {current_user.id}")
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        phoneNumber=current_user.phoneNumber,
        email=current_user.email,
        username=current_user.username,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        roles=[role.name for role in current_user.roles],
    )


async def get_current_user_with_roles(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current user from token, with roles and permissions eagerly loaded.

    Args:
        credentials: Bearer token credentials
        db: Database session

    Returns:
        Current user with roles and permissions

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode token
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"]
        )
        token_data = TokenPayload(**payload)

        # Check token type
        if token_data.type != "access":
            raise credentials_exception

        # Check if token is expired
        if token_data.exp is None:
            raise credentials_exception

        # Get id from token
        username: Optional[str] = token_data.sub
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Eagerly load roles and permissions
    result = await db.execute(
        select(User)
        .where(User.username == username)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
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
    current_user: User = Depends(get_current_user_with_roles),
    db: AsyncSession = Depends(get_db),
) -> bool:
    """
    Get current superuser.

    Args:
        current_user: Current user

    Returns:
        Current superuser

    Raises:
        HTTPException: If user is not superuser
    """
    try:
        user_service = UserService(db)
        user  = await user_service.get_by_username(current_user.username)
        return user is not None

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching user from database",
        )


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
        current_user: User = Depends(get_current_user_with_roles),
        db: AsyncSession = Depends(get_db),
        request: Request = None,
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
        if await get_current_superuser(current_user, db):
            return UserResponse(
                id=current_user.id,
                name=current_user.name,
                phoneNumber=current_user.phoneNumber,
                email=current_user.email,
                username=current_user.username,
                is_active=current_user.is_active,
                created_at=current_user.created_at,
                updated_at=current_user.updated_at,
                roles=[role.name for role in current_user.roles],
            )
        # Initialize ABAC Authorizer
        authorizer = ABAuthorizer(db)
        target = {}
        if request is None:
            # If request is not provided, assume it's a direct call
            target = {"response": "all"}
        else:
            if request.method == "POST" or request.method == "PUT":
                target = await request.json()
            elif request.method == "DELETE":
                target = request.path_params
            elif request.method == "GET":
                if "id" in request.path_params:
                    target = {"id": request.path_params["id"]}
                else:
                    target = {"response": "all"}

        is_allowed = await authorizer.is_allowed(resource, action, current_user, target)

        # User does not have permission
        if is_allowed:
            return UserResponse(
                id=current_user.id,
                name=current_user.name,
                phoneNumber=current_user.phoneNumber,
                email=current_user.email,
                username=current_user.username,
                is_active=current_user.is_active,
                created_at=current_user.created_at,
                updated_at=current_user.updated_at,
                roles=[role.name for role in current_user.roles],
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return check_permission