"""Permission service."""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import Permission
from src.app.schemas import PermissionCreate, PermissionUpdate


class PermissionService:
    """Permission service."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db

    async def get(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID."""
        query = select(Permission).where(Permission.id == permission_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        query = select(Permission).where(Permission.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[Permission]:
        """Get multiple permissions."""
        query = select(Permission).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, permission_in: PermissionCreate) -> Permission:
        """Create permission."""
        # Check if permission exists
        permission = await self.get_by_name(permission_in.name)
        if permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission with this name already exists",
            )

        # Create permission
        permission = Permission(**permission_in.model_dump())
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def update(
        self, permission: Permission, permission_in: PermissionUpdate
    ) -> Permission:
        """Update permission."""
        for field, value in permission_in.model_dump(exclude_unset=True).items():
            setattr(permission, field, value)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission

    async def delete(self, permission_id: int) -> None:
        """Delete permission."""
        permission = await self.get(permission_id)
        if permission:
            await self.db.delete(permission)
            await self.db.commit()
