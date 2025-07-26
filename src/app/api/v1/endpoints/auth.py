"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas import Login, RefreshToken, Token, UserResponse
from src.app.services import AuthService, UserService
from src.core.utils import create_rate_limiter
from src.core.db import get_db
from src.core.utils import file_upload_service

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    login_data: Login,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(create_rate_limiter(5, 60)),  # 5 requests per minute
) -> Token:
    """
    Login user.

    Args:
        login_data: Login credentials
        db: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    auth_service = AuthService(db)

    # Authenticate user
    user = await auth_service.authenticate(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens using username
    tokens = auth_service.create_tokens(user.username)
    return Token(**tokens)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: RefreshToken,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(create_rate_limiter(5, 60)),  # 5 requests per minute
) -> Token:
    """Refresh tokens."""
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_tokens(refresh_token.refresh_token)
    return Token(**tokens)


@router.post("/register", response_model=UserResponse)
async def register(
    name: str = Form(...),
    phoneNumber: str = Form(...),
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    photo: UploadFile = File(None),
    role_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user with role_id=2 (normal user).
    """
    photo_url = None
    if photo:
        file_info = await file_upload_service.save_file(photo, subfolder="userphotos")
        photo_url = file_upload_service.get_file_url(file_info["file_path"])
    user_data = {
        "name": name,
        "phoneNumber": phoneNumber,
        "email": email,
        "username": username,
        "password": password,
        "photo": photo_url,
    }
    user_service = UserService(db)
    user = await user_service.create_user_with_role(user_data, role_id=role_id)
    return UserResponse(
        id=user.id,
        name=user.name,
        phoneNumber=user.phoneNumber,
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        photo=user.photo,
        roles=[role.name for role in user.roles] if user.roles else [],
    )

