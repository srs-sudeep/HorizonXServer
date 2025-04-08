"""API v1 router."""
from fastapi import APIRouter

from src.app.api.v1.endpoints.auth import router as auth_router
from src.app.api.v1.endpoints.users import router as users_router
from src.app.api.v1.endpoints.rbac import router as rbac_router
from src.app.api.v1.endpoints.posts import router as posts_router

# Create API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(rbac_router, prefix="/rbac", tags=["rbac"])
api_router.include_router(posts_router, prefix="/posts", tags=["posts"])

