"""Middleware package."""
from src.core.middleware.cors import setup_cors_middleware
from src.core.middleware.logging import LoggingMiddleware

__all__ = ["setup_middleware", "LoggingMiddleware"]


def setup_middleware(app):
    """Set up all middleware."""
    # Setup CORS middleware
    setup_cors_middleware(app)
    
    # Setup logging middleware
    app.add_middleware(LoggingMiddleware)
