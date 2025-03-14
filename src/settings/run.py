import shutil
import subprocess
import sys
from pathlib import Path


def copy_env_file(env_type: str):
    """Copy the appropriate .env file based on environment type."""
    source = Path("envs") / f".env.{env_type}"
    target = Path(".env")

    if not source.exists():
        print(f"Error: {source} does not exist")
        sys.exit(1)

    shutil.copy2(source, target)
    print(f"Copied {source} to {target}")


def run_server(env_type: str):
    """Run the server with the specified environment."""
    copy_env_file(env_type)
    subprocess.run(["uvicorn", "src.app.main:app", "--reload"])


def dev_command():
    """Entry point for development server."""
    run_server("development")


def prod_command():
    """Entry point for production server."""
    run_server("production")

def ruff_lint():
    """Run ruff linter."""
    subprocess.run(["ruff", "check", "app/"])


def ruff_fix():
    """Run ruff linter."""
    subprocess.run(["ruff", "format", "app/"])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python settings/run.py [dev|prod|format|lint]")
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
    else:
        print("Invalid command. Use 'dev', 'prod', 'format', or 'lint'")
        sys.exit(1)
