@echo off
echo Installing latest packages with uv...

:: Create virtual environment if it doesn't exist
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate virtual environment
call .venv\Scripts\activate.bat

:: Install latest packages with uv
echo Installing latest packages with uv...
uv pip install -e .

echo Installation complete!
echo Run 'uv run dev' to start the development server.
