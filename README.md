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

This project implements a comprehensive Role-Based Access Control (RBAC) system that provides flexible and granular access control.

### Core Components

1. **Users**

   - Can have multiple roles
   - Can be superusers (bypass all permission checks)
   - Authenticated using JWT tokens

2. **Roles**

   - Named collections of permissions (e.g., "admin", "editor", "viewer")
   - Can have multiple permissions
   - Users can have multiple roles

3. **Permissions**
   - Defined by resource and action pairs (e.g., "posts:create", "users:read")
   - Can be assigned to roles
   - Superusers automatically have all permissions

### Permission Structure

Permissions follow the format: `resource:action`

Common actions include:

- `create`: Create new resources
- `read`: View resources
- `update`: Modify existing resources
- `delete`: Remove resources
- `*`: All actions on a resource

Examples:

```python
# Full access to posts
Permission(resource="posts", action="*")

# Read-only access to users
Permission(resource="users", action="read")

# Create and update products
Permission(resource="products", action="create")
Permission(resource="products", action="update")
```

### Usage Examples

1. **Protecting API Endpoints**

```python
from src.app.api.deps import has_permission

@router.post("/posts/")
async def create_post(
    post: PostCreate,
    current_user: User = Depends(has_permission("posts", "create"))
):
    # Only users with 'posts:create' permission can access this endpoint
    pass

@router.get("/users/")
async def list_users(
    current_user: User = Depends(has_permission("users", "read"))
):
    # Only users with 'users:read' permission can access this endpoint
    pass
```

2. **Creating Roles and Permissions**

```python
# Create an editor role
editor_role = Role(
    name="editor",
    description="Can manage blog posts"
)

# Add permissions to the role
editor_permissions = [
    Permission(resource="posts", action="create"),
    Permission(resource="posts", action="update"),
    Permission(resource="posts", action="read"),
]
editor_role.permissions.extend(editor_permissions)
```

3. **Assigning Roles to Users**

```python
# Assign editor role to user
user.roles.append(editor_role)
await db.commit()
```

### Built-in Roles

1. **Superuser**
   - Has all permissions
   - Created using `uv run createsuperuser`
   - Can manage other users and roles

### Managing RBAC

1. **Creating a Superuser**

```bash
# Using CLI
uv run createsuperuser

# Follow the prompts to enter email, username, and password
```

2. **API Endpoints for RBAC Management**

- `POST /api/v1/roles/` - Create new role
- `GET /api/v1/roles/` - List all roles
- `PUT /api/v1/roles/{role_id}` - Update role
- `DELETE /api/v1/roles/{role_id}` - Delete role
- `POST /api/v1/permissions/` - Create new permission
- `GET /api/v1/permissions/` - List all permissions
- `PUT /api/v1/permissions/{permission_id}` - Update permission
- `DELETE /api/v1/permissions/{permission_id}` - Delete permission

3. **Checking Permissions in Code**

```python
# Check if user has specific permission
for role in user.roles:
    for permission in role.permissions:
        if permission.resource == "posts" and permission.action == "create":
            # User has permission to create posts
            pass

# Using the dependency
from src.app.api.deps import has_permission

@router.post("/posts/")
async def create_post(
    current_user: User = Depends(has_permission("posts", "create"))
):
    # Only accessible to users with posts:create permission
    pass
```

### Best Practices

1. **Permission Naming**

   - Use lowercase for resources and actions
   - Use descriptive names (e.g., "user_profiles" instead of "profiles")
   - Be consistent with action names (create, read, update, delete)

2. **Role Design**

   - Follow the principle of least privilege
   - Create roles based on job functions
   - Avoid giving more permissions than necessary
   - Document role purposes and permissions

3. **Security Considerations**
   - Regularly audit role assignments
   - Remove unused roles and permissions
   - Keep superuser access limited
   - Log permission checks and role changes

## Rate Limits

Rate limiting can be configured in the `.env` file:

- **Enable/Disable Rate Limiting**: Set `RATE_LIMIT_ENABLED` to `true` or `false`.
- **Default Rate Limit**: Set `RATE_LIMIT_DEFAULT` to a value like `100/minute` (100 requests per minute).

Example configuration in `.env.development`:

```env
# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute
```

### Usage in Code

The rate limiter is implemented as a dependency that can be added to any FastAPI route. For example:

```python
from fastapi import APIRouter, Depends
from src.core.utils.rate_limit import create_rate_limiter

router = APIRouter()

@router.get("/example")
async def example_endpoint(
    _: None = Depends(create_rate_limiter(5, 60)),  # 5 requests per minute
):
    return {"message": "This endpoint is rate-limited."}
```

### Headers for Rate Limit Information

When rate limiting is enabled, the following headers are added to responses:

- `X-RateLimit-Limit`: The maximum number of requests allowed.
- `X-RateLimit-Remaining`: The number of requests remaining in the current time window.
- `X-RateLimit-Reset`: The time (in seconds) until the rate limit resets.

### Example Response

If a client exceeds the rate limit, they will receive a `429 Too Many Requests` response:

```json
{
  "detail": "Too many requests"
}
```

## Caching

This project includes a caching mechanism to improve performance by reducing redundant computations or database queries. It uses Redis as the backend for caching.

### How It Works

- The `fastapi-cache` library is used to implement caching.
- A decorator `cached` is provided to cache the results of API endpoints or functions.
- Cache keys can be customized using a `key_builder` function.
- User-specific cache keys can be generated using the `user_specific_cache_key` utility.

### Configuration

Caching can be configured in the `.env` file:

- **Redis URL**: Set `REDIS_URL` to the Redis connection string.

Example configuration in `.env.development`:

```env
# Redis configuration
REDIS_URL=redis://localhost:6379/0
```

### Usage in Code

1. **Basic Caching**:
   Use the `cached` decorator to cache the results of an API endpoint or function. For example:

   ```python
   from fastapi import APIRouter
   from src.core.cache.utils import cached

   router = APIRouter()

   @router.get("/example")
   @cached(expire=60)  # Cache for 60 seconds
   async def example_endpoint():
       return {"message": "This response is cached."}
   ```

2. **Custom Cache Keys**:
   Use the `user_specific_cache_key` utility to create user-specific cache keys. For example:

   ```python
   from fastapi import APIRouter
   from src.core.cache.utils import cached, user_specific_cache_key

   router = APIRouter()

   @router.get("/user-data")
   @cached(expire=120, key_builder=user_specific_cache_key)  # Cache for 120 seconds
   async def user_data_endpoint():
       return {"message": "This response is cached per user."}
   ```

3. **Custom Key Builder**:
   You can define your own key builder function to customize cache keys. For example:

   ```python
   def custom_key_builder(func, namespace: str = "", **kwargs):
       return f"{namespace}:{func.__name__}:custom_key"

   @router.get("/custom-cache")
   @cached(expire=30, key_builder=custom_key_builder)  # Cache for 30 seconds
   async def custom_cache_endpoint():
       return {"message": "This response uses a custom cache key."}
   ```

### Cache Invalidation

To invalidate a cache entry, you can use the `fastapi-cache` API to delete the corresponding key from Redis.

### Example Response

When caching is enabled, subsequent requests to the same endpoint will return the cached response until the cache expires.

```json
{
  "message": "This response is cached."
}
```

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
