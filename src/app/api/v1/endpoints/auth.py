"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.schemas.auth import Login, RefreshToken, Token
from src.app.services.auth import AuthService
from src.core.utils.rate_limit import create_rate_limiter
from src.core.db.session import get_db

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







