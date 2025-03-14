

# FastAPI Template

A modern FastAPI template with environment management and development tools.

## Requirements

- Python 3.13+
- uv (Python package installer and resolver)

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd fastapi-template
```

2. Install dependencies using uv:
```bash
uv pip install -e .
```

## Project Structure

```
fastapi-template/
├── app/
│   ├── __init__.py
│   └── main.py          # Main FastAPI application
├── envs/
│   ├── .env.development # Development environment variables
│   └── .env.production  # Production environment variables
├── scripts/
│   ├── __init__.py
│   └── manage.py        # Management commands
├── .gitignore
├── .python-version      # Python version specification
├── pyproject.toml       # Project configuration
├── README.md
└── uv.lock             # Dependency lock file
```

## Available Commands

Run the development server:
```bash
uv run dev
```

Run the production server:
```bash
uv run prod
```

Format code using Black:
```bash
uv run format
```

## API Endpoints

- `GET /`: Returns a hello world message
- `POST /getdata/`: Accepts JSON data with a "content" field and logs it to a file

## Environment Variables

### Development (.env.development)
```env
APP_ENV=development
DEBUG=true
HOST=127.0.0.1
PORT=8000
RELOAD=true
```

### Production (.env.production)
```env
APP_ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=8000
RELOAD=false
```

## CORS Configuration

Currently configured to accept requests from all origins (`*`). Modify the `origins` list in `app/main.py` for your specific needs:

```python
origins = [
    "*",  # Replace with your allowed domains
]
```

## Dependencies

- FastAPI (with all standard extras)
- Black (code formatter)
- uvicorn (ASGI server)
- python-dotenv (environment management)

## Development

1. Run the development server:
```bash
uv run dev
```

2. Access the API documentation:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Production

1. Run the production server:
```bash
uv run prod
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Format your code (`uv run format`)
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

[Your chosen license]