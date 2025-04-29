"""Role model for RBAC."""

from typing import List, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, relationship
from src.core.db import Base

if TYPE_CHECKING:
    # Avoid circular import
    from src.app.models.user import User
    from src.app.models.permission import Permission

# Role-Permission association table
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permission.id"), primary_key=True),
)


class Role(Base):
    """Role model."""

    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    # Relationships
    users: Mapped[List["User"]] = relationship(  # type: ignore
        "User", secondary="user_role", back_populates="roles"
    )
    permissions: Mapped[List["Permission"]] = relationship(  # type: ignore
        "Permission", secondary=role_permission, back_populates="roles"
    )
