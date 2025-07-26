from src.app.api.v1.endpoints.file_serving import router as file_router
from src.app.api.v1.endpoints.auth import router as auth_router
from src.app.api.v1.endpoints.rbac import router as rbac_router
from src.app.api.v1.endpoints.users import router as users_router
from src.app.api.v1.endpoints.module import router as module_router
from src.app.api.v1.endpoints.route import router as route_router
from src.app.api.v1.endpoints.sidebar import router as sidebar_router

__all__ = [
    "file_router"
    "auth_router",
    "rbac_router",
    "users_router",
    "module_router",
    "route_router",
    "sidebar_router",
]
