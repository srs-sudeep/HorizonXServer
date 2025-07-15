"""User service."""

from typing import Optional
from sqlalchemy import or_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from src.app.models import User, Role
from src.app.schemas import UserWithRoles, UserResponse
from src.core.security import verify_password
from .base import BaseService


class UserService(BaseService[User]):
    """User service."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        super().__init__(db, User)

    async def get_by_ldapid(self, ldapid: str) -> Optional[UserResponse]:
        """Get user by LDAP ID."""
        query = (
            select(User).where(User.ldapid == ldapid).options(selectinload(User.roles))
        )
        result = await self.db.execute(query)
        user_obj = result.scalar_one_or_none()
        return user_obj

    async def get_by_idNumber(self, idNumber: str) -> Optional[UserResponse]:
        """Get user by ID Number."""
        query = (
            select(User)
            .where(User.idNumber == idNumber)
            .options(selectinload(User.roles))
        )
        result = await self.db.execute(query)
        user_obj = result.scalar_one_or_none()
        return user_obj

    async def get_by_superadmin(self, ldapid: str) -> Optional[UserResponse]:
        query = (
            select(User)
            .join(User.roles)
            .where(User.ldapid == ldapid, Role.name == "admin")
        )
        result = await self.db.execute(query)
        user_obj = result.scalar_one_or_none()
        return user_obj

    async def create(
        self,
        *,
        ldapid: str,
        idNumber: str,
        name: str,
        is_active: bool = True,
        roles=None,
    ) -> User:
        """Async create method for User with optional roles."""
        if roles is None:
            roles = []
        user = User(
            ldapid=ldapid,
            idNumber=idNumber,
            name=name,
            is_active=is_active,
            roles=roles,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_user_if_not_exists(self, user: UserWithRoles) -> User:
        """Create new user if not exists."""
        existing_user = await self.get_by_ldapid(user["ldapid"])
        if existing_user is not None:
            return existing_user
        roles = []
        print(f"Creating user with LDAP ID: {user['ldapid']}")
        print(f"User details: {user['roles']}")
        if "roles" in user and user["roles"]:
            for name in user["roles"]:
                print(f"Creating role for user: {name}")
                result = await self.db.execute(select(Role).where(Role.name == name))
                role_obj = result.scalar_one_or_none()
                print(f"Role object: {role_obj}")
                if role_obj:
                    roles.append(role_obj)
        user_obj = await self.create(
            ldapid=user["ldapid"],
            idNumber=user["idNumber"],
            name=user["name"],
            is_active=user.get("is_active", True),
            roles=roles,
        )
        return user_obj

    async def authenticate(self, ldapid: str, password: str) -> Optional[User]:
        """Authenticate user."""
        user = await self.get_by_ldapid(ldapid)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def validate_user_roles(self, user: User) -> bool:
        """
        Validate if the user has roles assigned.

        Args:
            user: The user object to validate.

        Raises:
            HTTPException: If the user has no roles assigned.
        """
        # Ensure roles are eagerly loaded
        user = await self.get_by_ldapid(user.ldapid)
        if not user.roles or len(user.roles) == 0:
            print(f"User {user.ldapid} has no roles assigned.")
            return False
        return True

    async def get_all_with_all_roles(self):
        """Get all users with their roles and all available roles."""
        # Get all users with their roles
        users_query = select(User).options(selectinload(User.roles))
        users_result = await self.db.execute(users_query)
        users = users_result.scalars().all()

        # Get all roles
        roles_query = select(Role)
        roles_result = await self.db.execute(roles_query)
        all_roles = roles_result.scalars().all()

        # Build the response
        user_list = []
        for user in users:
            user_role_ids = {role.role_id for role in user.roles}
            roles_with_assigned = [
                {
                    "role_id": role.role_id,
                    "name": role.name,
                    "isAssigned": role.role_id in user_role_ids,
                }
                for role in all_roles
            ]
            user_list.append(
                {
                    "ldapid": user.ldapid,
                    "idNumber": user.idNumber,
                    "name": user.name,
                    "is_active": user.is_active,
                    "roles": roles_with_assigned,
                }
            )
        return user_list

    async def add_role(self, user_id: str, role_id: int):
        """Add a role to a user."""
        result = await self.db.execute(
            select(User).where(User.ldapid == user_id).options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()
        role = await self.db.get(Role, role_id)
        if not user or not role:
            raise HTTPException(status_code=404, detail="User or Role not found")
        if role not in user.roles:
            user.roles.append(role)
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def remove_role(self, user_id: int, role_id: int):
        """Remove a role from a user."""
        result = await self.db.execute(
            select(User).where(User.ldapid == user_id).options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()
        role = await self.db.get(Role, role_id)
        if not user or not role:
            raise HTTPException(status_code=404, detail="User or Role not found")
        if role in user.roles:
            user.roles.remove(role)
            await self.db.commit()
            await self.db.refresh(user)
        return user

    async def get_all_users_with_filters(
        self,
        search: str = None,
        status: bool = None,
        roles: list[int] = None,
        limit: int = 10,
        offset: int = 0,
        all_roles: list[Role] = None,
    ):
        query = select(User).options(selectinload(User.roles))

        # Text search
        if search:
            search_pattern = f"%{search.lower()}%"
            query = query.where(
                or_(
                    func.lower(User.name).like(search_pattern),
                    func.lower(User.ldapid).like(search_pattern),
                    func.lower(User.idNumber).like(search_pattern),
                    User.roles.any(func.lower(Role.name).like(search_pattern)),
                )
            )

        # Status filter
        if status is not None:
            query = query.where(User.is_active == status)

        # Role filter (multi-select)
        if roles:
            query = query.where(User.roles.any(Role.role_id.in_(roles)))

        count_query = query.with_only_columns(func.count(User.ldapid)).order_by(None)
        total_count = (await self.db.execute(count_query)).scalar_one()

        # Pagination
        query = query.offset(offset).limit(limit)
        users_result = await self.db.execute(query)
        users = users_result.scalars().unique().all()

        # Build the response
        user_list = []
        for user in users:
            user_role_ids = {role.role_id for role in user.roles}
            roles_with_assigned = [
                {
                    "role_id": role.role_id,
                    "name": role.name,
                    "isAssigned": role.role_id in user_role_ids,
                }
                for role in (all_roles or [])
            ]
            user_list.append(
                {
                    "ldapid": user.ldapid,
                    "idNumber": user.idNumber,
                    "name": user.name,
                    "is_active": user.is_active,
                    "roles": roles_with_assigned,
                }
            )
        return {"total_count": total_count, "users": user_list}