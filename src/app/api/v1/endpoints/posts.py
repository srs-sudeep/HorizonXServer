"""Blog post endpoints with RBAC."""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.api.deps import get_db, has_permission
from src.app.models.user import User
from src.app.schemas.post import Post, PostCreate, PostUpdate
from src.app.services.post import PostService

router = APIRouter()

@router.post("/", response_model=Post)
async def create_post(
    post_in: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("posts", "create")),
) -> Post:
    """Create new post."""
    post_service = PostService(db)
    return await post_service.create(post_in, current_user)

@router.get("/", response_model=List[Post])
async def list_posts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("posts", "read")),
) -> List[Post]:
    """List posts."""
    post_service = PostService(db)
    return await post_service.get_multi(skip=skip, limit=limit)

@router.get("/{post_id}", response_model=Post)
async def get_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("posts", "read")),
) -> Post:
    """Get post by ID."""
    post_service = PostService(db)
    post = await post_service.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/{post_id}", response_model=Post)
async def update_post(
    post_id: int,
    post_in: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("posts", "update")),
) -> Post:
    """Update post."""
    post_service = PostService(db)
    post = await post_service.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await post_service.update(post, post_in)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("posts", "delete")),
) -> None:
    """Delete post."""
    post_service = PostService(db)
    post = await post_service.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await post_service.delete(post_id)