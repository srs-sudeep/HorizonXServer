@echo off
echo Initializing database...

:: Set environment variables
set DATABASE_URL=postgresql+asyncpg://postgres:1234@localhost:5432/fastapi_dev

:: Run migrations
uv run alembic revision --autogenerate -m "Initial migration"
uv run alembic upgrade head

echo Database initialization complete!