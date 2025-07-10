from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.app.models import Module, Role, route_role
from src.app.schemas import SidebarModuleItem, SidebarRouteItem
from src.app.services import RouteService, RoleService


class SidebarService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sidebar(self, role: str = None, is_active: bool = None):
        # Fetch all modules
        modules_result = await self.db.execute(select(Module))
        modules = modules_result.scalars().all()

        # If role filter is provided, get role_id
        role_id = None
        if role:
            role_result = await self.db.execute(select(Role).where(Role.name == role))
            role_obj = role_result.scalar_one_or_none()
            if role_obj:
                role_id = role_obj.role_id

        route_service = RouteService(self.db)
        if role_id:
            routes = await route_service.get_routes_by_role_ids(
                [role_id], is_active=is_active, is_sidebar=True
            )
        else:
            routes = await route_service.get_all()

        role_service = RoleService(self.db)
        all_roles = await role_service.get_all()

        # Build a mapping of role_id to role_name
        role_map = {role.role_id: role.name for role in all_roles}

        # Build a mapping of route_id to list of role_ids using the association table
        route_role_result = await self.db.execute(select(route_role))
        route_role_pairs = route_role_result.fetchall()
        route_roles_map = {}
        for row in route_role_pairs:
            route_id = row.route_id
            role_id = row.role_id
            route_roles_map.setdefault(route_id, []).append(role_id)

        # Group routes by module_id
        routes_by_module = {}
        for route in routes:
            routes_by_module.setdefault(route.module_id, []).append(route)

        # Helper to build nested route tree
        def build_route_tree(routes, parent_id=None):
            items = []
            for route in routes:
                if route.parent_id == parent_id:
                    children = build_route_tree(routes, parent_id=route.id)
                    roles_data = [
                        {"role_id": str(rid), "role_name": role_map.get(rid, "")}
                        for rid in route_roles_map.get(route.id, [])
                    ]
                    items.append(
                        SidebarRouteItem(
                            id=route.id,
                            label=route.label,
                            path=route.path,
                            icon=route.icon,
                            isActive=route.is_active,
                            is_sidebar=route.is_sidebar,
                            parent_id=route.parent_id,
                            module_id=route.module_id,
                            children=children,
                            roles=roles_data,
                        )
                    )
            return items

        sidebar = []
        for module in modules:
            module_routes = routes_by_module.get(module.id, [])
            submodules = build_route_tree(module_routes, parent_id=None)
            if role:
                if submodules:
                    sidebar.append(
                        SidebarModuleItem(
                            id=module.id,
                            label=module.label,
                            icon=module.icon,
                            isActive=module.is_active,
                            subModules=submodules,
                        )
                    )
            else:
                sidebar.append(
                    SidebarModuleItem(
                        id=module.id,
                        label=module.label,
                        icon=module.icon,
                        isActive=module.is_active,
                        subModules=submodules,
                    )
                )
        return sidebar
