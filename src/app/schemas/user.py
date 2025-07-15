"""User schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Base User schema
class UserBase(BaseModel):
    """Base User schema."""

    ldapid: str = Field(
        ..., min_length=1, max_length=255, description="LDAP ID of the user"
    )
    name: str = Field(..., min_length=1, description="Name of the user")
    idNumber: str = Field(..., min_length=1, description="ID number of the user")
    is_active: bool = True


# User creation schema
class UserCreate(UserBase):
    """User creation schema."""


# User update schema
class UserUpdate(BaseModel):
    """User update schema."""

    is_active: Optional[bool] = None


# User in DB schema
class UserInDB(UserBase):
    """User in DB schema."""

    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# User response schema
class User(UserInDB):
    """User response schema."""

    pass


class UserResponse(User):
    """User response schema for API responses."""

    roles: Optional[List[str]] = Field(
        default=None, description="Roles assigned to the user"
    )


class UserRole(BaseModel):
    role_id: Optional[int]
    name: str

    model_config = {"from_attributes": True}


class UserWithRoles(BaseModel):
    ldapid: str
    idNumber: str
    name: str
    is_active: bool
    roles: List[UserRole]

    model_config = {"from_attributes": True}


class UserRoleWithAssigned(BaseModel):
    role_id: int
    name: str
    isAssigned: bool

    model_config = {"from_attributes": True}


class UserWithAllRoles(BaseModel):
    ldapid: str
    idNumber: str
    name: str
    is_active: bool
    roles: List[UserRoleWithAssigned]

    model_config = {"from_attributes": True}