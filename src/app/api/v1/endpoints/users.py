"""User endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, func
from src.core.db import get_db
from src.app.services import UserService, RoleService
from src.app.schemas import (
    UserResponse,
    UserWithRoles,
    UserComponentAdd,
    UserComponentRemove,
    UserComponentList,
    UserComponentQuery,
)
from src.app.api import get_current_user, has_permission
from src.app.models import User, Role

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user info."""
    # roles = [role.name for role in current_user.roles]
    # print(f"Current user roles: {current_user}")
    return current_user


@router.get("/")
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("users", "read")),
    search: str = Query(None, description="Search text"),
    status: bool = Query(None, description="Filter by active status"),
    roles: list[int] = Query(None, description="Filter by role ids"),
    limit: int = Query(10, ge=1, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset"),
):
    role_service = RoleService(db)
    all_roles = await role_service.get_all()
    user_service = UserService(db)
    return await user_service.get_all_users_with_filters(
        search=search,
        status=status,
        roles=roles,
        limit=limit,
        offset=offset,
        all_roles=all_roles,
    )


@router.post("/{user_id}/roles/{role_id}", response_model=UserWithRoles)
async def add_role_to_user(
    user_id: str,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("users", "update")),
):
    service = UserService(db)
    user = await service.add_role(user_id, role_id)
    return UserWithRoles.from_orm(user)


@router.delete("/{user_id}/roles/{role_id}", response_model=UserWithRoles)
async def remove_role_from_user(
    user_id: str,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("users", "update")),
):
    service = UserService(db)
    user = await service.remove_role(user_id, role_id)
    return UserWithRoles.from_orm(user)


@router.get("/user/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("users", "read")),
):
    service = UserService(db)
    user = await service.get_by_id(user_id)
    if not user:
        user = await service.get_by_email(user_id)
    if not user:
        user = await service.get_by_username(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    roles = [role.name for role in user.roles]
    return UserResponse(
        id=user.id,
        name=user.name,
        phoneNumber=user.phoneNumber,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=roles,
    )


@router.get("/filters")
async def get_user_filters(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("users", "read")),
):
    # Fetch all roles
    roleservice = RoleService(db)
    roles = await roleservice.get_all()
    role_options = [{"role_id": role.role_id, "name": role.name} for role in roles]

    status_options = [
        {"label": "Active", "value": True},
        {"label": "Inactive", "value": False},
    ]

    return {
        "roles": role_options,
        "status": status_options,
    }


@router.post("/add-component", response_model=UserComponentAdd)
async def add_component_to_user(
    data: UserComponentAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("users", "update")),
):
    service = UserService(db)
    return await service.add_component_to_user(data.user_id, data.component_id)


@router.delete("/remove-component", response_model=UserComponentRemove)
async def remove_component_from_user(
    data: UserComponentRemove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("users", "update")),
):
    service = UserService(db)
    return await service.remove_component_from_user(data.user_id, data.component_id)


@router.get("/components", response_model=UserComponentList)
async def get_components_by_user(
    user_id: str = Query(None, description="User ID to fetch components for"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("users", "read")),
):
    service = UserService(db)
    target_user_id = user_id if user_id is not None else current_user.id
    return await service.get_components_by_user(target_user_id)