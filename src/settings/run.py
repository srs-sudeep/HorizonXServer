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


def ruff_format() -> None:
    """Run ruff formatter in check mode (show what would be formatted)."""
    subprocess.run(
        [
            "ruff",
            "format",
            "--check",
            "--diff",
            "src/",
            "--exclude",
            "*.pyc,__pycache__,.pytest_cache,.git,.venv,.ruff_cache,build,dist,*.egg-info",
        ]
    )


def ruff_format_fix() -> None:
    """Run ruff formatter and fix the files."""
    subprocess.run(
        [
            "ruff",
            "format",
            "src/",
            "--exclude",
            "*.pyc,__pycache__,.pytest_cache,.git,.venv,.ruff_cache,build,dist,*.egg-info",
        ]
    )


def ruff_lint_fix() -> None:
    """Run ruff linter."""
    subprocess.run(["ruff", "check", "src/", "--fix"])


def makemigrations() -> None:
    """Generate new database migrations."""
    # Copy development environment file
    copy_env_file("development")

    # Get migration message from user
    message = input("Enter migration message: ").strip()
    if not message:
        print("Migration message cannot be empty")
        sys.exit(1)

    # Generate new migration
    result = subprocess.run(
        ["alembic", "revision", "--autogenerate", "-m", message],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✅ Successfully generated new migration")
        print("\nGenerated files:")
        # Extract migration file names from output
        for line in result.stdout.split("\n"):
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
        ["alembic", "upgrade", "head"], capture_output=True, text=True
    )

    if result.returncode == 0:
        print("✅ Successfully applied migrations")
    else:
        print("❌ Failed to apply migrations")
        print("\nError:")
        print(result.stderr)
        sys.exit(1)

def pre_commit() -> None:
    try:
        subprocess.run(["pre-commit", "install"], check=True)
        print("Pre-commit hooks installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error installing pre-commit hooks: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
        
def commit() -> None:
    
    import subprocess

    try:
        # Run pre-commit hooks
        print("Running pre-commit hooks...")
        subprocess.run(["pre-commit", "run", "--all-files"], check=True)

        # Stage all changes
        print("Staging changes...")
        subprocess.run(["git", "add", "."], check=True)

        # Run commitizen
        print("Running commitizen...")
        subprocess.run(["cz", "commit"], check=True)

        print("✅ Commit process completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ An error occurred: {e}")
        exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python -m src.settings.run [dev|prod|format|format-fix|lint|lint-fix|makemigrations|migrate]"
        )
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "dev":
        dev_command()
    elif command == "prod":
        prod_command()
    elif command == "format":
        ruff_format()
    elif command == "format-fix":
        ruff_format_fix()
    elif command == "lint":
        ruff_lint()
    elif command == "lint-fix":
        ruff_lint_fix()
    elif command == "makemigrations":
        makemigrations()
    elif command == "migrate":
        migrate()
    elif command == "pre-commit":
        pre_commit()
    elif command == "commit":
        commit()
    else:
        print(
            "Invalid command. Use 'dev', 'prod', 'format','format-fix', 'lint','lint-fix', 'makemigrations','pre-commit','commit', or 'migrate'"
        )
        sys.exit(1)
