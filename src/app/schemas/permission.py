"""Permission schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# Base Permission schema
class PermissionBase(BaseModel):
    """Base Permission schema."""

    name: str
    description: Optional[str] = None
    resource: str
    action: str
    expression: Optional[dict] = None


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
    expression: Optional[dict] = None


# Permission in DB schema
class PermissionInDB(PermissionBase):
    """Permission in DB schema."""

    permission_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Permission response schema
class Permission(PermissionInDB):
    """Permission response schema."""

    pass


class PermissionWithSelected(BaseModel):
    permission_id: int
    name: str
    description: Optional[str] = None
    resource: str
    action: str
    selected: bool
    expression: Optional[dict] = None

    class Config:
        from_attributes = True
