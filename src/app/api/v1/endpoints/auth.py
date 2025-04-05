"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.app.schemas.auth import Login, RefreshToken, Token
from src.app.services.auth import AuthService
from src.core.utils.rate_limit import create_rate_limiter

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(),
    _: None = Depends(create_rate_limiter(5, 60)),  # 5 requests per minute
) -> Token:
    """
    Login user.

    Args:
        form_data: OAuth2 form data
        auth_service: Authentication service

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user
    user = await auth_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    tokens = auth_service.create_tokens(user.id)
    return Token(**tokens)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: RefreshToken,
    auth_service: AuthService = Depends(),
    _: None = Depends(create_rate_limiter(5, 60)),  # 5 requests per minute
) -> Token:
    """
    Refresh tokens.

    Args:
        refresh_token: Refresh token
        auth_service: Authentication service

    Returns:
        New access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Refresh tokens
    tokens = await auth_service.refresh_tokens(refresh_token.refresh_token)
    return Token(**tokens)
