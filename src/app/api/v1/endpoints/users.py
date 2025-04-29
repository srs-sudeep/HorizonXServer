"""User endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.app.api import get_current_user
from src.app.models import User
from src.app.schemas import UserCreate
from src.app.schemas.user import User as UserResponse
from src.app.services import UserService

router = APIRouter()


@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create new user."""
    user_service = UserService(db)
    existing_user = await user_service.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_service.create_user(user_in)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current user info."""
    return current_user
