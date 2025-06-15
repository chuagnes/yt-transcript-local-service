#!/bin/bash

set -e

VENV_DIR="venv"

echo "🔍 Checking for virtual environment..."

# Check if already activated
if [[ -n "$VIRTUAL_ENV" ]]; then
  echo "✅ Virtual environment is already active: $VIRTUAL_ENV"
else
  # Check if venv directory exists
  if [[ -d "$VENV_DIR" ]]; then
    echo "🔁 Found existing virtual environment in ./$VENV_DIR"
  else
    echo "📦 Creating new virtual environment in ./$VENV_DIR"
    python3 -m venv "$VENV_DIR"
  fi

  # Activate the virtual environment
  echo "⚙️ Activating virtual environment..."
  source "$VENV_DIR/bin/activate"
  echo "✅ Virtual environment activated."
fi

# Install dependencies
echo "📜 Installing dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ All dependencies installed successfully."
