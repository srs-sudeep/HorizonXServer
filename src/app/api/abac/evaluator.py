from src.app.api.abac.engine import ABACEngine
from src.app.services import PermissionService


class ABAuthorizer:
    def __init__(self, db):
        self.policy_service = PermissionService(db)

    async def is_allowed(self, resource, action, actor, target):
        roles = [role.name for role in actor.roles]

        permissions = await self.policy_service.get_policies(roles, resource, action)
        print(
            f"Checking permissions for actor: {actor.id}, resource: {resource}, action: {action}"
        )

        # Extract actor fields for ABAC context
        actor_context = {
            "id": actor.id,
            "name": actor.name,
            "email": actor.email,
            "username": actor.username,
            "is_active": actor.is_active,
            "is_superuser": actor.is_superuser,
            "roles": roles,
        }

        context = {"actor": actor_context, "target": target}

        for permission in permissions:
            if permission.expression is None:
                return True
            engine = ABACEngine(context)
            if engine.evaluate(permission.expression):
                return True

        return False