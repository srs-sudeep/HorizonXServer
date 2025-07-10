"""Role model for RBAC."""

from typing import List, TYPE_CHECKING
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, relationship
from src.core.db import Base

if TYPE_CHECKING:
    # Avoid circular import
    from src.app.models.user import User
    from src.app.models.permission import Permission
    from src.app.models.route import Route

# Role-Permission association table
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("role.role_id"), primary_key=True),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permission.permission_id"),
        primary_key=True,
    ),
)


class Role(Base):
    """Role model."""

    role_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True, nullable=False
    )
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    # Relationships
    users: Mapped[List["User"]] = relationship(  # type: ignore
        "User", secondary="user_role", back_populates="roles"
    )
    permissions: Mapped[List["Permission"]] = relationship(  # type: ignore
        "Permission", secondary=role_permission, back_populates="roles"
    )
    routes: Mapped[List["Route"]] = relationship(  # type: ignore
        "Route", secondary="route_role", back_populates="roles"
    )
