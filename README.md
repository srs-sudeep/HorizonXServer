# FastAPI Boilerplate

A comprehensive FastAPI boilerplate with SQLAlchemy, PostgreSQL, Redis caching, rate limiting, and RBAC.

## Features

- **FastAPI** - High-performance web framework
- **SQLAlchemy** - Async ORM with PostgreSQL support
- **Alembic** - Database migrations
- **Redis** - Caching and rate limiting
- **RBAC** - Role-based access control
- **Docker** - Containerization
- **Environment Management** - Separate development and production environments
- **UV** - Fast Python package installer

## Requirements

- Python 3.13+
- UV (Python package installer and resolver)
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL (for local development)
- Redis (for local development)
  - **Note for Windows users**: Redis doesn't officially support Windows. Use WSL (Windows Subsystem for Linux) or Docker. See [Running Redis on Windows Using WSL](#running-redis-on-windows-using-wsl) section below.

## Project Structure

```
fastapi-boilerplate/
├── src/
│   ├── app/
│   │   ├── api/              # API routes
│   │   │   ├── v1/           # API version 1
│   │   │   │   ├── endpoints/  # API endpoints
│   │   │   │   └── router.py  # API router
│   │   │   ├── deps.py       # API dependencies
│   │   │   └── router.py     # Main API router
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── main.py           # FastAPI application
│   ├── core/
│   │   ├── cache/            # Redis cache
│   │   ├── db/               # Database
│   │   ├── utils/            # Utilities
│   │   ├── config.py         # Configuration
│   │   ├── exceptions.py     # Exception handlers
│   │   ├── logging.py        # Logging configuration
│   │   ├── middleware.py     # Middleware
│   │   └── security.py       # Security utilities
│   └── settings/
│       └── run.py            # Run script
├── envs/                     # Environment variables
├── migrations/               # Alembic migrations
├── tests/                    # Tests
├── .env                      # Environment variables (copied from envs)
├── .gitignore                # Git ignore file
├── alembic.ini               # Alembic configuration
├── docker-compose.yml        # Docker Compose configuration
├── Dockerfile                # Docker configuration
├── pyproject.toml            # Project configuration
└── README.md                 # Project documentation
```

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <your-repository-url>
cd fastapi-boilerplate
```

2. Install dependencies using UV (this will install the latest versions of all packages):
```bash
# On Windows
install_latest.bat

# On Unix/Linux/Mac
python -m venv .venv
source .venv/bin/activate
uv pip install -e .
```

3. Set up PostgreSQL and Redis locally or using Docker:
```bash
docker-compose up -d postgres redis
```

4. Initialize the database:
```bash
uv run init-db
```

5. Run the development server:
```bash
uv run dev
```

### Docker Deployment

1. Build and run the Docker containers:
```bash
docker-compose up -d
```

## Available Commands

- Run the development server:
```bash
uv run dev
```

- Run the production server:
```bash
uv run prod
```

- Format code using Ruff:
```bash
uv run format
```

- Lint code using Ruff:
```bash
uv run lint
```

- Initialize the database:
```bash
uv run init-db
```

## Package Management

This project uses UV along with Poetry for package management. UV is a fast Python package installer and resolver.

- Install all packages defined in pyproject.toml:
```bash
uv pip install -e .
```

- Add a new package:
```bash
uv pip install package_name
```
Then add it to the dependencies list in pyproject.toml.

## Running Redis on Windows Using WSL

Redis doesn't officially support Windows. The recommended approach is to use Windows Subsystem for Linux (WSL).

### 1. Install WSL

1. Open PowerShell as Administrator and run:
```powershell
wsl --install
```

2. Restart your computer when prompted.

3. After restart, a Ubuntu terminal will open. Set up your Linux username and password.

### 2. Install Redis on WSL

1. Open your WSL terminal (Ubuntu) and update the package lists:
```bash
sudo apt update
```

2. Install Redis:
```bash
sudo apt install redis-server
```

3. Start the Redis service:
```bash
sudo service redis-server start
```

4. Verify Redis is running:
```bash
redis-cli ping
```
If Redis is running correctly, it should respond with "PONG".

### 3. Configure Redis for External Access

1. Edit the Redis configuration file:
```bash
sudo nano /etc/redis/redis.conf
```

2. Find the line with `bind 127.0.0.1 ::1` and change it to `bind 0.0.0.0` to allow connections from Windows.

3. Find the line that contains `supervised no` and change it to `supervised systemd`.

4. Save and exit (Ctrl+O, Enter, Ctrl+X).

5. Restart Redis:
```bash
sudo systemctl restart redis-server
```

### 4. Connect to Redis from Your Application

Update your `.env.development` file to point to the WSL Redis instance:
```
REDIS_URL=redis://localhost:6379/0
```

### 5. Starting and Stopping Redis

Start Redis:
```bash
sudo service redis-server start
```

Stop Redis:
```bash
sudo service redis-server stop
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

The application uses environment variables for configuration. These are stored in the `envs/` directory and copied to `.env` when running the application.

### Development (.env.development)

```env
# Application settings
APP_ENV=development
DEBUG=true
HOST=127.0.0.1
PORT=8000
RELOAD=true
LOG_LEVEL=DEBUG
SECRET_KEY=dev_secret_key_change_in_production

# Database settings
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_dev

# Redis settings
REDIS_URL=redis://localhost:6379/0

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute

# CORS settings
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Production (.env.production)

```env
# Application settings
APP_ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
RELOAD=false
LOG_LEVEL=INFO
SECRET_KEY=your_production_secret_key_here

# Database settings
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/fastapi_prod

# Redis settings
REDIS_URL=redis://redis:6379/0

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=60/minute

# CORS settings
CORS_ORIGINS=https://yourdomain.com
```

## Authentication

The application uses JWT tokens for authentication. The following endpoints are available:

- `POST /api/v1/auth/login` - Login with username and password
- `POST /api/v1/auth/refresh` - Refresh access token

## Role-Based Access Control (RBAC)

The application uses a role-based access control system with the following models:

- `User` - User model with roles
- `Role` - Role model with permissions
- `Permission` - Permission model with resource and action

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Format your code (`uv run format`)
4. Lint your code (`uv run lint`)
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

[MIT License](LICENSE)