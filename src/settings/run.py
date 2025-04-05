"""Run script for the application."""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def copy_env_file(env_type: str) -> None:
    """Copy the appropriate .env file based on environment type."""
    source = Path("envs") / f".env.{env_type}"
    target = Path(".env")

    if not source.exists():
        print(f"Error: {source} does not exist")
        sys.exit(1)

    shutil.copy2(source, target)
    print(f"Copied {source} to {target}")


def run_server(env_type: str) -> None:
    """Run the server with the specified environment."""
    # Copy environment file
    copy_env_file(env_type)

    # Load environment variables from the copied .env file
    from dotenv import load_dotenv
    load_dotenv()

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"

    # Base command
    cmd = [
        "uvicorn",
        "src.app.main:app",
        f"--host={host}",
        f"--port={port}",
    ]

    if reload:
        cmd.append("--reload")

    subprocess.run(cmd)


def dev_command() -> None:
    """Entry point for development server."""
    run_server("development")


def prod_command() -> None:
    """Entry point for production server."""
    run_server("production")


def ruff_lint() -> None:
    """Run ruff linter."""
    subprocess.run(["ruff", "check", "src/"])


def ruff_fix() -> None:
    """Run ruff formatter."""
    subprocess.run(["ruff", "format", "src/"])


def makemigrations() -> None:
    """Generate new database migrations."""
    # Copy development environment file
    copy_env_file("development")

    # Generate new migration
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", "Auto-generated migration"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ Successfully generated new migration")
        print("\nGenerated files:")
        # Extract migration file names from output
        for line in result.stdout.split('\n'):
            if "migrations/versions/" in line:
                print(f"  {line.strip()}")
    else:
        print("❌ Failed to generate migration")
        print("\nError:")
        print(result.stderr)
        sys.exit(1)


def migrate() -> None:
    """Apply database migrations."""
    # Copy development environment file
    copy_env_file("development")

    # Apply migrations
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ Successfully applied migrations")
    else:
        print("❌ Failed to apply migrations")
        print("\nError:")
        print(result.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.settings.run [dev|prod|format|lint|makemigrations|migrate]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "dev":
        dev_command()
    elif command == "prod":
        prod_command()
    elif command == "format":
        ruff_fix()
    elif command == "lint":
        ruff_lint()
    elif command == "makemigrations":
        makemigrations()
    elif command == "migrate":
        migrate()
    else:
        print("Invalid command. Use 'dev', 'prod', 'format', 'lint', 'makemigrations', or 'migrate'")
        sys.exit(1)



