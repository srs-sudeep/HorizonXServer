from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from sqlalchemy.orm import selectinload
from src.app.schemas import RouteResponse
from src.app.models import Route, Role, route_component


class RouteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_orm(self, route_id: int):
        result = await self.db.execute(
            select(Route).where(Route.id == route_id).options(selectinload(Route.roles))
        )
        return result.scalar_one_or_none()

    async def get(self, route_id: int):
        route = await self._get_orm(route_id)
        if not route:
            return None
        return RouteResponse(
            id=route.id,
            path=route.path,
            label=route.label,
            icon=route.icon,
            is_active=route.is_active,
            is_sidebar=route.is_sidebar,
            module_id=route.module_id,
            parent_id=route.parent_id,
            role_ids=[role.role_id for role in getattr(route, "roles", [])],
        )

    async def get_all(self):
        result = await self.db.execute(select(Route).options(selectinload(Route.roles)))
        routes = result.scalars().all()
        return [
            RouteResponse(
                id=route.id,
                path=route.path,
                label=route.label,
                icon=route.icon,
                is_active=route.is_active,
                is_sidebar=route.is_sidebar,
                module_id=route.module_id,
                parent_id=route.parent_id,
                role_ids=[role.role_id for role in getattr(route, "roles", [])],
            )
            for route in routes
        ]

    async def create(
        self,
        path: str,
        label: str,
        module_id: int,
        is_active: bool = True,
        is_sidebar: bool = True,
        icon: str = None,
        parent_id: int = None,
        role_ids=None,
    ):
        route = Route(
            path=path,
            label=label,
            icon=icon,
            is_sidebar=is_sidebar,
            is_active=is_active,
            module_id=module_id,
            parent_id=parent_id,
        )
        roles = []
        if role_ids:
            roles = (
                (await self.db.execute(select(Role).where(Role.role_id.in_(role_ids))))
                .scalars()
                .all()
            )
            route.roles = roles
        self.db.add(route)
        await self.db.commit()
        await self.db.refresh(route)
        return RouteResponse(
            id=route.id,
            path=route.path,
            label=route.label,
            icon=route.icon,
            is_active=route.is_active,
            is_sidebar=route.is_sidebar,
            module_id=route.module_id,
            parent_id=route.parent_id,
            role_ids=[role.role_id for role in roles],
        )

    async def update(self, route_id: int, **kwargs):
        route = await self._get_orm(route_id)
        if not route:
            return None
        if "role_ids" in kwargs and kwargs["role_ids"] is not None:
            roles = (
                (
                    await self.db.execute(
                        select(Role).where(Role.role_id.in_(kwargs["role_ids"]))
                    )
                )
                .scalars()
                .all()
            )
            route.roles = roles
            del kwargs["role_ids"]
        for key, value in kwargs.items():
            setattr(route, key, value)
        await self.db.commit()
        await self.db.refresh(route)
        return RouteResponse(
            id=route.id,
            path=route.path,
            label=route.label,
            icon=route.icon,
            is_active=route.is_active,
            is_sidebar=route.is_sidebar,
            module_id=route.module_id,
            parent_id=route.parent_id,
            role_ids=[role.role_id for role in getattr(route, "roles", [])],
        )

    async def delete(self, route_id: int):
        route = await self._get_orm(route_id)
        if not route:
            return None
        await self.db.delete(route)
        await self.db.commit()
        return True

    async def get_routes_by_role_ids(
        self, role_ids, is_active: bool = None, is_sidebar: bool = None
    ):
        stmt = select(Route).options(selectinload(Route.roles))
        if is_active is not None:
            stmt = stmt.where(Route.is_active == is_active)
        if is_sidebar is not None:
            stmt = stmt.where(Route.is_sidebar == is_sidebar)
        result = await self.db.execute(stmt)
        routes = result.scalars().all()
        filtered_routes = [
            route
            for route in routes
            if any(role.role_id in role_ids for role in getattr(route, "roles", []))
        ]
        return [
            RouteResponse(
                id=route.id,
                path=route.path,
                label=route.label,
                icon=route.icon,
                is_active=route.is_active,
                is_sidebar=route.is_sidebar,
                module_id=route.module_id,
                parent_id=route.parent_id,
                role_ids=[role.role_id for role in getattr(route, "roles", [])],
            )
            for route in filtered_routes
        ]

    async def add_component_to_route(self, route_id: int, component_id: str):
        await self.db.execute(
            insert(route_component).values(route_id=route_id, component_id=component_id)
        )
        await self.db.commit()
        return {"route_id": route_id, "component_id": component_id}

    async def remove_component_from_route(self, route_id: int, component_id: str):
        await self.db.execute(
            delete(route_component).where(
                route_component.c.route_id == route_id,
                route_component.c.component_id == component_id,
            )
        )
        await self.db.commit()
        return {"route_id": route_id, "component_id": component_id}

    async def get_components_by_route(self, route_id: int):
        result = await self.db.execute(
            select(route_component.c.component_id).where(route_component.c.route_id == route_id)
        )
        component_ids = [row[0] for row in result.fetchall()]
        return {"route_id": route_id, "component_ids": component_ids}
