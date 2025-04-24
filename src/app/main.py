"""Main application module."""

from dotenv import load_dotenv

from src.app.setup import create_app

# Load environment variables
load_dotenv()

# Create FastAPI application
app = create_app()
