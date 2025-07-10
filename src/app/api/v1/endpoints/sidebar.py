from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.app.services.sidebar import SidebarService
from src.app.schemas.sidebar import SidebarModuleItem
from src.app.models import User
from src.app.api import has_permission

router = APIRouter()


@router.get("/sidebar", response_model=list[SidebarModuleItem])
async def get_sidebar(
    role: str = Query(None, description="Role name to filter routes"),
    is_active: bool = Query(None, description="Filter by isActive flag (True/False)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("module", "read")),
):
    service = SidebarService(db)
    return await service.get_sidebar(role=role, is_active=is_active)
