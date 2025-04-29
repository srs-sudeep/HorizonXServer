"""User schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Base User schema
class UserBase(BaseModel):
    """Base User schema."""

    email: EmailStr
    username: str
    is_active: bool = True


# User creation schema
class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)


# User update schema
class UserUpdate(BaseModel):
    """User update schema."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


# User in DB schema
class UserInDB(UserBase):
    """User in DB schema."""

    id: int
    created_at: datetime
    updated_at: datetime
    is_superuser: bool = False

    class Config:
        """Pydantic config."""

        from_attributes = True


# User response schema
class User(UserInDB):
    """User response schema."""

    pass
