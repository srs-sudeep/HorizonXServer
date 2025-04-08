"""Models package."""
from src.app.models.permission import Permission
from src.app.models.post import Post
from src.app.models.role import Role
from src.app.models.user import User

__all__ = ["User", "Role", "Permission", "Post"]
