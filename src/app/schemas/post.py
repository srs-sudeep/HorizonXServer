"""Blog post schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PostBase(BaseModel):
    """Base Post schema."""

    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    """Post creation schema."""

    pass


class PostUpdate(BaseModel):
    """Post update schema."""

    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


class PostInDB(PostBase):
    """Post in DB schema."""

    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class Post(PostInDB):
    """Post response schema."""

    pass
