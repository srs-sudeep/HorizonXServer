"""User schemas."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Base User schema
class UserBase(BaseModel):
    """Base User schema."""

    name: str = Field(..., min_length=1, description="Name of the user")
    phoneNumber: str = Field(..., min_length=1, description="Phone number of the user")
    email: str = Field(..., description="Email of the user")
    username: str = Field(..., min_length=1, description="Username of the user")
    photo: Optional[str] = None
    is_active: bool = True


# User creation schema
class UserCreate(UserBase):
    """User creation schema."""
    
    password: str = Field(..., min_length=8, description="Password for the user")
    is_superuser: bool = False


# User update schema
class UserUpdate(BaseModel):
    """User update schema."""

    name: Optional[str] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


# User in DB schema
class UserInDB(UserBase):
    """User in DB schema."""

    id: str
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
    id: str
    name: str
    phoneNumber: str
    email: str
    username: str
    is_active: bool
    roles: List[UserRole]

    model_config = {"from_attributes": True}


class UserRoleWithAssigned(BaseModel):
    role_id: int
    name: str
    isAssigned: bool

    model_config = {"from_attributes": True}


class UserWithAllRoles(BaseModel):
    id: str
    name: str
    phoneNumber: str
    email: str
    username: str
    is_active: bool
    roles: List[UserRoleWithAssigned]

    model_config = {"from_attributes": True}


class UserComponentAdd(BaseModel):
    user_id: str
    component_id: str


class UserComponentRemove(BaseModel):
    user_id: str
    component_id: str


class UserComponentList(BaseModel):
    user_id: str
    component_ids: List[str]

class UserRouteBase(BaseModel):
    route_id: str
    has_access: bool = Field(default=False)

class UserRouteCreate(UserRouteBase):
    user_id: str

class UserRouteResponse(UserRouteBase):
    user_id: str

    class Config:
        orm_mode = True

class UserRoutesList(BaseModel):
    user_id: str
    routes: List[UserRouteResponse]