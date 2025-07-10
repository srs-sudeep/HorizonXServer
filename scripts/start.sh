#!/bin/bash

# Database initialization script
# This script runs migrations and creates superadmin user automatically

echo "🚀 Starting FastAPI application with database initialization..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
python -c "
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from src.core.config import settings

async def wait_for_db():
    engine = create_async_engine(str(settings.DATABASE_URL))
    for i in range(30):
        try:
            async with engine.begin() as conn:
                await conn.execute('SELECT 1')
            print('✅ Database is ready!')
            return
        except Exception as e:
            print(f'⏳ Database not ready, waiting... ({i+1}/30)')
            await asyncio.sleep(2)
    print('❌ Database connection failed!')
    sys.exit(1)

asyncio.run(wait_for_db())
"

# Run database migrations
echo "📦 Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# Initialize database with superadmin and permissions
echo "🔧 Initializing database with superadmin and permissions..."
python scripts/init_database.py

if [ $? -eq 0 ]; then
    echo "✅ Database initialization completed successfully"
else
    echo "❌ Database initialization failed"
    exit 1
fi

# Start the FastAPI application
echo "🌟 Starting FastAPI application..."
exec uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
