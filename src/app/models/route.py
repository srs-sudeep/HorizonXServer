from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship, Mapped, backref
from src.core.db import Base

if TYPE_CHECKING:
    from src.app.models.role import Role
# Association table for route-role many-to-many
route_role = Table(
    "route_role",
    Base.metadata,
    Column("route_id", Integer, ForeignKey("route.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("role.role_id"), primary_key=True),
)


class Route(Base):
    __tablename__ = "route"
    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String, unique=True, nullable=False, index=True)
    label = Column(String, nullable=False)
    icon = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_sidebar = Column(Boolean, default=True)
    module_id = Column(Integer, ForeignKey("module.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("route.id"), nullable=True)

    module = relationship("Module", backref="routes")
    parent = relationship(
        "Route",
        remote_side=[id],
        backref=backref("children", cascade="all, delete-orphan"),
    )
    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary=route_role, back_populates="routes"
    )
