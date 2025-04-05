"""Base service class with common database operations."""
from typing import Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")

class BaseService(Generic[ModelType]):
    """Base class for all services."""

    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model

    async def get(self, id: int) -> Optional[ModelType]:
        """Get by id."""
        query = select(self.model).where(self.model.id == id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ModelType]:
        """Get all records."""
        query = select(self.model)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        """Create new record."""
        db_obj = self.model(**kwargs)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """Update record."""
        db_obj = await self.get(id)
        if db_obj:
            for key, value in kwargs.items():
                setattr(db_obj, key, value)
            await self.db.commit()
            await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        """Delete record."""
        db_obj = await self.get(id)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
            return True
        return False