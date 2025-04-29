"""Post service."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models import Post,User
from src.app.schemas import PostCreate, PostUpdate


class PostService:
    """Post service."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db

    async def get(self, post_id: int) -> Optional[Post]:
        """Get post by ID."""
        query = select(Post).where(Post.id == post_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[Post]:
        """Get multiple posts."""
        query = select(Post).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, post_in: PostCreate, author: User) -> Post:
        """Create post."""
        post = Post(**post_in.model_dump(), author_id=author.id)
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def update(self, post: Post, post_in: PostUpdate) -> Post:
        """Update post."""
        for field, value in post_in.model_dump(exclude_unset=True).items():
            setattr(post, field, value)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def delete(self, post_id: int) -> None:
        """Delete post."""
        post = await self.get(post_id)
        if post:
            await self.db.delete(post)
            await self.db.commit()
