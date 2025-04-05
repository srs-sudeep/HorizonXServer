#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing UV..."
pip install uv

echo "Installing project dependencies..."
uv pip install --upgrade pip
uv pip install -e ".[unix]"

echo "Installation complete!"