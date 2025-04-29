"""Post model."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship
from src.core.db import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular import
    from src.app.models.user import User


class Post(Base):
    """Post model."""

    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, default=True)
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    # Relationships
    author: Mapped["User"] = relationship("User", back_populates="posts")  # type: ignore
