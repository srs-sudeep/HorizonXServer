"""RBAC management endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.deps import get_current_superuser, get_db, has_permission
from src.app.models.user import User
from src.app.schemas.permission import Permission, PermissionCreate, PermissionUpdate
from src.app.schemas.role import Role, RoleCreate, RoleUpdate
from src.app.services.permission import PermissionService
from src.app.services.role import RoleService

router = APIRouter()


# Role endpoints
@router.post("/roles", response_model=Role)
async def create_role(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("roles", "create")),
) -> Role:
    """Create new role."""
    role_service = RoleService(db)
    return await role_service.create(role_in)


@router.get("/roles", response_model=List[Role])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("roles", "read")),
) -> List[Role]:
    """List roles."""
    role_service = RoleService(db)
    return await role_service.get_multi(skip=skip, limit=limit)


@router.get("/roles/{role_id}", response_model=Role)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("roles", "read")),
) -> Role:
    """Get role by ID."""
    role_service = RoleService(db)
    role = await role_service.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/roles/{role_id}", response_model=Role)
async def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("roles", "update")),
) -> Role:
    """Update role."""
    role_service = RoleService(db)
    role = await role_service.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return await role_service.update(role, role_in)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("roles", "delete")),
) -> None:
    """Delete role."""
    role_service = RoleService(db)
    role = await role_service.get(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    await role_service.delete(role_id)


# Permission endpoints
@router.post("/permissions", response_model=Permission)
async def create_permission(
    permission_in: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("permissions", "create")),
) -> Permission:
    """Create new permission."""
    permission_service = PermissionService(db)
    return await permission_service.create(permission_in)


@router.get("/permissions", response_model=List[Permission])
async def list_permissions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("permissions", "read")),
) -> List[Permission]:
    """List permissions."""
    permission_service = PermissionService(db)
    return await permission_service.get_multi(skip=skip, limit=limit)


@router.get("/permissions/{permission_id}", response_model=Permission)
async def get_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("permissions", "read")),
) -> Permission:
    """Get permission by ID."""
    permission_service = PermissionService(db)
    permission = await permission_service.get(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.put("/permissions/{permission_id}", response_model=Permission)
async def update_permission(
    permission_id: int,
    permission_in: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("permissions", "update")),
) -> Permission:
    """Update permission."""
    permission_service = PermissionService(db)
    permission = await permission_service.get(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return await permission_service.update(permission, permission_in)


@router.delete("/permissions/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("permissions", "delete")),
) -> None:
    """Delete permission."""
    permission_service = PermissionService(db)
    permission = await permission_service.get(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    await permission_service.delete(permission_id)


# Role-Permission management
@router.post("/roles/{role_id}/permissions/{permission_id}")
async def add_permission_to_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("roles", "update")),
) -> Role:
    """Add permission to role."""
    role_service = RoleService(db)
    return await role_service.add_permission(role_id, permission_id)


@router.delete("/roles/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("roles", "update")),
) -> Role:
    """Remove permission from role."""
    role_service = RoleService(db)
    return await role_service.remove_permission(role_id, permission_id)
