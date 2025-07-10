from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.app.api import has_permission
from src.app.schemas import RouteCreate, RouteUpdate, RouteResponse
from src.app.services import RouteService, RoleService
from src.app.models import User

router = APIRouter()


@router.post("/", response_model=RouteResponse)
async def create_route(
    data: RouteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("route", "create")),
):
    service = RouteService(db)
    route = await service.create(**data.dict())
    return route


@router.get("/", response_model=list[RouteResponse])
async def list_routes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("route", "read")),
):
    service = RouteService(db)
    return await service.get_all()


@router.get("/indi/{route_id}", response_model=RouteResponse)
async def get_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("route", "read")),
):
    service = RouteService(db)
    route = await service.get(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.get("/my-routes", response_model=list[RouteResponse])
async def get_my_routes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("route", "read")),
):
    service = RouteService(db)
    roles = RoleService(db)
    role_names = getattr(current_user, "roles", [])
    if isinstance(role_names, str):
        role_names = [role_names]
    user_role_ids = []
    for role_name in role_names:
        role = await roles.get_by_name(role_name)
        if role:
            user_role_ids.append(role.role_id)
    return await service.get_routes_by_role_ids(user_role_ids)


@router.put("/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: int,
    data: RouteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("route", "update")),
):
    service = RouteService(db)
    route = await service.update(route_id, **data.dict(exclude_unset=True))
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(has_permission("route", "delete")),
):
    service = RouteService(db)
    route = await service.delete(route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
