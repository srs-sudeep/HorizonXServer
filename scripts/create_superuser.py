"""Script to create a superuser with all permissions."""
import asyncio
import getpass
import re
import sys
import uuid
from pathlib import Path
from typing import Optional

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.models.role import Role
from src.app.models.permission import Permission
from src.app.services.user import UserService
from src.core.db.session import async_session_factory
from src.core.security import get_password_hash
from src.core.config import settings


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """Validate username format."""
    pattern = r"^[a-zA-Z0-9_-]{3,32}$"
    return bool(re.match(pattern, username))


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid, message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is valid"


def get_input(prompt: str, validator: Optional[callable] = None, error_msg: str = "") -> str:
    while True:
        value = input(prompt).strip()
        if not value:
            print("This field is required.")
            continue
        if validator and not validator(value):
            print(error_msg or "Invalid input.")
            continue
        return value


def get_password() -> str:
    while True:
        password = getpass.getpass("Password: ")
        if not password:
            print("Password is required.")
            continue
        is_valid, message = validate_password(password)
        if not is_valid:
            print(f"Invalid password: {message}")
            continue
        password2 = getpass.getpass("Password (again): ")
        if password != password2:
            print("Passwords don't match!")
            continue
        return password


async def ensure_superuser_role(session: AsyncSession) -> Role:
    """Ensure superuser role exists with all permissions."""
    # Check if superuser role exists
    query = select(Role).where(Role.name == "superuser")
    result = await session.execute(query)
    superuser_role = result.scalar_one_or_none()

    if not superuser_role:
        print("\n📦 Creating superuser role and permissions...")
        superuser_role = Role(
            name="superuser",
            description="Superuser role with all permissions"
        )
        session.add(superuser_role)

        # Create all permissions
        permissions = [
            Permission(
                name="all",
                resource="*",
                action="*",
                description="All permissions"
            )
        ]
        session.add_all(permissions)
        superuser_role.permissions.extend(permissions)
        await session.commit()
        print("✅ Superuser role created successfully")
    else:
        print("\n✅ Superuser role already exists")

    return superuser_role


async def create_superuser_async(session: AsyncSession, email: str, username: str, name: str, phoneNumber: str, password: str) -> None:
    """Create a superuser with all permissions."""
    try:
        # Check if user already exists
        user_service = UserService(session)
        existing_user = await user_service.get_by_email(email)
        if existing_user:
            print(f"\n❌ User with email {email} already exists!")
            return

        # Ensure superuser role exists
        superuser_role = await ensure_superuser_role(session)

        # Create superuser
        print("\n👤 Creating superuser account...")
        user = await user_service.create(
            id=str(uuid.uuid4()),
            email=email,
            username=username,
            name=name,
            phoneNumber=phoneNumber,
            hashed_password=get_password_hash(password),
            is_superuser=True,
            is_active=True,
        )
        user.roles.append(superuser_role)
        await session.commit()

        print(f"\n✅ Superuser '{username}' created successfully!")
        print(f"Email: {email}")
        print("You can now log in using these credentials.")

    except Exception as e:
        print(f"\n❌ Error creating superuser: {str(e)}")
        await session.rollback()
        raise


async def create_superuser() -> None:
    """Create a superuser with all permissions."""
    print("\n=== Create Superuser ===\n")
    email = get_input("Email: ", validator=validate_email, error_msg="Please enter a valid email address.")
    username = get_input("Username: ", validator=validate_username, error_msg="Username must be 3-32 characters long and contain only letters, numbers, underscores, and hyphens.")
    name = get_input("Name: ")
    phoneNumber = get_input("Phone Number: ")
    password = get_password()

    async with async_session_factory() as session:
        try:
            await create_superuser_async(session, email, username, name, phoneNumber, password)
        except Exception as e:
            print(f"\n❌ Failed to create superuser: {str(e)}")
            sys.exit(1)


def main() -> None:
    """Main function."""
    try:
        # Create event loop
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Run the async function
        asyncio.run(create_superuser())
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

