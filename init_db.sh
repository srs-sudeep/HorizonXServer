#!/bin/bash
echo "Initializing database..."

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_db"

# Run migrations
alembic upgrade head

echo "Database initialization complete!"