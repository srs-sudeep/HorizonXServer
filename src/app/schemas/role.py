"""Role schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Base Role schema
class RoleBase(BaseModel):
    """Base Role schema."""

    name: str
    description: Optional[str] = None


# Role creation schema
class RoleCreate(RoleBase):
    """Role creation schema."""

    pass


# Role update schema
class RoleUpdate(BaseModel):
    """Role update schema."""

    name: Optional[str] = None
    description: Optional[str] = None


# Role in DB schema
class RoleInDB(RoleBase):
    """Role in DB schema."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Role response schema
class Role(RoleInDB):
    """Role response schema."""

    pass
