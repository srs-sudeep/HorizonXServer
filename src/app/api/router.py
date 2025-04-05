"""API router."""
from fastapi import APIRouter

from src.app.api.v1.router import api_router as api_v1_router
from src.core.config import settings

# Create API router
api_router = APIRouter()

# Include API versions
api_router.include_router(api_v1_router, prefix=settings.API_V1_STR)
