from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.app.models.module import Module


class ModuleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, module_id: int):
        return await self.db.get(Module, module_id)

    async def get_all(self):
        result = await self.db.execute(select(Module))
        return result.scalars().all()

    async def create(
        self, name: str, label: str, icon: str = None, is_active: bool = True
    ):
        module = Module(name=name, label=label, icon=icon, is_active=is_active)
        self.db.add(module)
        await self.db.commit()
        await self.db.refresh(module)
        return module

    async def update(self, module_id: int, **kwargs):
        module = await self.get(module_id)
        if not module:
            return None
        for key, value in kwargs.items():
            setattr(module, key, value)
        await self.db.commit()
        await self.db.refresh(module)
        return module

    async def delete(self, module_id: int):
        module = await self.get(module_id)
        if not module:
            return None
        await self.db.delete(module)
        await self.db.commit()
        return module
