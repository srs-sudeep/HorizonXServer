"""User model."""

from typing import List, TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, relationship

from src.core.db import Base

if TYPE_CHECKING:
    from src.app.models.role import Role

# User-Role association table
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", String, ForeignKey("user.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("role.role_id"), primary_key=True),
)


class User(Base):
    """User model."""
    __tablename__ = "user"
    
    id = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String, nullable=False)
    phoneNumber = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=user_role, back_populates="users"
    )
