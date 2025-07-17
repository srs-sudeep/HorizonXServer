"""Schemas package."""

from src.app.schemas.auth import Login, RefreshToken, Token, TokenPayload
from src.app.schemas.permission import (
    Permission,
    PermissionCreate,
    PermissionInDB,
    PermissionUpdate,
    PermissionWithSelected,
)
from src.app.schemas.role import Role, RoleCreate, RoleInDB, RoleUpdate
from src.app.schemas.user import User, UserCreate, UserInDB, UserUpdate,UserBase, UserResponse,UserRole,UserWithRoles, UserWithAllRoles, UserRoleWithAssigned, UserComponentAdd, UserComponentRemove, UserComponentList
from src.app.schemas.module import (
    ModuleBase,
    ModuleCreate,
    ModuleResponse,
    ModuleUpdate,
)
from src.app.schemas.route import RouteBase, RouteCreate, RouteResponse, RouteUpdate, RouteComponentAdd, RouteComponentRemove, RouteComponentList
from src.app.schemas.sidebar import SidebarModuleItem, SidebarRouteItem, SidebarComponentItem

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "User"
    "UserBase",
    "UserResponse",
    "UserRole",
    "UserWithRoles",
    "UserWithAllRoles",
    "UserRoleWithAssigned",
    "UserComponentAdd",
    "UserComponentRemove",
    "UserComponentList",
    "Role",
    "RoleCreate",
    "RoleUpdate",
    "RoleInDB",
    "Permission",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionInDB",
    "PermissionWithSelected",
    "Token",
    "TokenPayload",
    "Login",
    "RefreshToken",
    "ModuleBase",
    "ModuleCreate",
    "ModuleUpdate",
    "ModuleResponse",
    "RouteBase",
    "RouteCreate",
    "RouteUpdate",
    "RouteResponse",
    "RouteComponentAdd",
    "RouteComponentRemove",
    "RouteComponentList",
    "SidebarModuleItem",
    "SidebarRouteItem",
    "SidebarComponentItem",
]
