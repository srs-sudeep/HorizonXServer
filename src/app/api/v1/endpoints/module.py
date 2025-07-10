from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.models import User
from src.core.db import get_db
from src.app.api import has_permission
from src.app.schemas import ModuleCreate, ModuleUpdate, ModuleResponse
from src.app.services import ModuleService

router = APIRouter()


@router.post("/", response_model=ModuleResponse)
async def create_module(
    data: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("module", "create")),
):
    service = ModuleService(db)
    module = await service.create(**data.dict())
    return module


@router.get("/", response_model=list[ModuleResponse])
async def list_modules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("module", "read")),
):
    service = ModuleService(db)
    return await service.get_all()


@router.get("/indi/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("module", "read")),
):
    service = ModuleService(db)
    module = await service.get(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: int,
    data: ModuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("module", "update")),
):
    service = ModuleService(db)
    module = await service.update(module_id, **data.dict(exclude_unset=True))
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("module", "delete")),
):
    service = ModuleService(db)
    module = await service.delete(module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
