"""Script to create a superuser."""
import asyncio
import getpass
import sys
from pathlib import Path

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


def get_input(prompt: str, required: bool = True) -> str:
    """Get input from user with validation."""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("This field is required.")


def get_password() -> str:
    """Get password input with confirmation."""
    while True:
        password = getpass.getpass("Password: ")
        if not password:
            print("Password is required.")
            continue
            
        password2 = getpass.getpass("Password (again): ")
        if password != password2:
            print("Passwords don't match!")
            continue
            
        return password


async def create_superuser_async(session: AsyncSession, email: str, username: str, password: str) -> None:
    """Create a superuser with all permissions."""
    # Check if user already exists
    user_service = UserService(session)
    existing_user = await user_service.get_by_email(email)
    if existing_user:
        print(f"\n❌ User with email {email} already exists!")
        return

    # Get or create superuser role
    query = select(Role).where(Role.name == "superuser")
    result = await session.execute(query)
    superuser_role = result.scalar_one_or_none()

    if not superuser_role:
        print("\nCreating superuser role and permissions...")
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

    # Create superuser
    print("\nCreating superuser account...")
    user = await user_service.create(
        email=email,
        username=username,
        hashed_password=get_password_hash(password),
        is_superuser=True,
        is_active=True,
    )

    # Add superuser role
    user.roles.append(superuser_role)
    await session.commit()

    print(f"\n✅ Superuser '{username}' created successfully!")


async def create_superuser() -> None:
    """Create a superuser with all permissions."""
    print("\n=== Create Superuser ===\n")
    
    # Get user input
    email = get_input("Email: ")
    username = get_input("Username: ")
    password = get_password()

    async with async_session_factory() as session:
        try:
            await create_superuser_async(session, email, username, password)
        except Exception as e:
            await session.rollback()
            raise e


def main() -> None:
    """Main function."""
    try:
        # Create event loop
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # Run the async function
        asyncio.run(create_superuser())
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

