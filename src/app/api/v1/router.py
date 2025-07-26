"""API v1 router."""

from fastapi import APIRouter

from src.app.api.v1.endpoints import (
    file_router,
    auth_router,
    rbac_router,
    users_router,
    module_router,
    route_router,
    sidebar_router,
)

# Create API router
router = APIRouter()

# Include endpoint routers
router.include_router(file_router,prefix = "/file",tags = ["file"])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(users_router, prefix="/users", tags=["users"])
router.include_router(rbac_router, prefix="/rbac", tags=["rbac"])
router.include_router(module_router, prefix="/module", tags=["module"])
router.include_router(route_router, prefix="/route", tags=["route"])
router.include_router(sidebar_router, prefix="/sidebar", tags=["sidebar"])
