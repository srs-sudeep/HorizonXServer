"""Authentication schemas."""
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """Token schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class Login(BaseModel):
    """Login schema."""

    username: str
    password: str


class RefreshToken(BaseModel):
    """Refresh token schema."""

    refresh_token: str

