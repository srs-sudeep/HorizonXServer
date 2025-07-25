"""Role service."""

from typing import List, Optional, Union

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.models import Role, Permission
from src.app.schemas import RoleCreate, RoleUpdate
from src.core.db import get_db


class RoleService:
    """Role service."""

    def __init__(self, db: AsyncSession = Depends(get_db)):
        """
        Initialize role service.

        Args:
            db: Database session
        """
        self.db = db

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        """
        Get role by ID.

        Args:
            role_id: Role ID

        Returns:
            Role or None
        """
        query = (
            select(Role)
            .where(Role.role_id == role_id)
            .options(selectinload(Role.permissions))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Role]:
        """
        Get role by name.

        Args:
            name: Role name

        Returns:
            Role or None
        """
        query = (
            select(Role)
            .where(Role.name == name)
            .options(selectinload(Role.permissions))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, role_in: RoleCreate) -> Role:
        """
        Create role.

        Args:
            role_in: Role creation data

        Returns:
            Created role

        Raises:
            HTTPException: If role with name already exists
        """
        # Check if role with name already exists
        role = await self.get_by_name(role_in.name)
        if role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists",
            )

        # Create role
        role = Role(
            name=role_in.name,
            description=role_in.description,
        )
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def update(self, role: Role, role_in: Union[RoleUpdate, dict]) -> Role:
        """
        Update role.

        Args:
            role: Role to update
            role_in: Role update data

        Returns:
            Updated role
        """
        # Convert to dict if not already
        update_data = (
            role_in
            if isinstance(role_in, dict)
            else role_in.model_dump(exclude_unset=True)
        )

        # Update role
        for field, value in update_data.items():
            if hasattr(role, field) and value is not None:
                setattr(role, field, value)

        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role

    async def delete(self, role: Role) -> None:
        """
        Delete role.

        Args:
            role: Role to delete
        """
        await self.db.delete(role)
        await self.db.commit()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """
        Get all roles.

        Args:
            skip: Number of roles to skip
            limit: Maximum number of roles to return

        Returns:
            List of roles
        """
        query = (
            select(Role)
            .options(selectinload(Role.permissions))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        roles = result.scalars().all()
        print(roles)
        return list(roles)

    async def add_permission(self, role_id: int, permission_id: int) -> Role:
        """
        Add a permission to a role.

        Args:
            role_id: Role ID
            permission_id: Permission ID

        Returns:
            Updated role

        Raises:
            HTTPException: If role or permission not found
        """
        # Fetch the role and permission
        role = await self.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        permission_query = select(Permission).where(
            Permission.permission_id == permission_id
        )
        result = await self.db.execute(permission_query)
        permission = result.scalar_one_or_none()
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        # Add permission if not already present
        if permission not in role.permissions:
            role.permissions.append(permission)
            self.db.add(role)
            await self.db.commit()
            await self.db.refresh(role)
        return role

    async def remove_permission(self, role_id: int, permission_id: int) -> Role:
        """
        Remove a permission from a role.

        Args:
            role_id: Role ID
            permission_id: Permission ID

        Returns:
            Updated role

        Raises:
            HTTPException: If role or permission not found
        """
        # Fetch the role and permission
        role = await self.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        permission_query = select(Permission).where(
            Permission.permission_id == permission_id
        )
        result = await self.db.execute(permission_query)
        permission = result.scalar_one_or_none()
        if not permission:
            raise HTTPException(status_code=404, detail="Permission not found")

        # Remove permission if present
        if permission in role.permissions:
            role.permissions.remove(permission)
            self.db.add(role)
            await self.db.commit()
            await self.db.refresh(role)
        return role
