"""Permission schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Base Permission schema
class PermissionBase(BaseModel):
    """Base Permission schema."""

    name: str
    description: Optional[str] = None
    resource: str
    action: str


# Permission creation schema
class PermissionCreate(PermissionBase):
    """Permission creation schema."""

    pass


# Permission update schema
class PermissionUpdate(BaseModel):
    """Permission update schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None


# Permission in DB schema
class PermissionInDB(PermissionBase):
    """Permission in DB schema."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Permission response schema
class Permission(PermissionInDB):
    """Permission response schema."""

    pass
