"""Permission model for RBAC."""
from typing import List, Optional

from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, relationship

from src.core.db.base import Base


class Permission(Base):
    """Permission model."""

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    resource = Column(String, nullable=False)
    action = Column(String, nullable=False)

    # Relationships
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary="role_permission", back_populates="permissions"
    )
