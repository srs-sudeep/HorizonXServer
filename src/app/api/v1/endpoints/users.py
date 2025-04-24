"""User endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.deps import get_current_user, get_db
from src.app.models.user import User
from src.app.schemas import UserCreate, User
from src.app.services.user import UserService

router = APIRouter()


@router.post("/", response_model=User)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Create new user."""
    user_service = UserService(db)
    existing_user = await user_service.get_by_email(user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await user_service.create_user(user_in)


@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current user info."""
    return current_user
