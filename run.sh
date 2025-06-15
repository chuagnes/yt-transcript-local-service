#!/bin/bash

set -e

VENV_DIR="venv"

echo "🔍 Checking for virtual environment..."

# If already activated, use it
if [[ -n "$VIRTUAL_ENV" ]]; then
  echo "✅ Virtual environment already active: $VIRTUAL_ENV"
else
  # Check for venv directory
  if [[ -d "$VENV_DIR" ]]; then
    echo "🔁 Found existing virtual environment in ./$VENV_DIR"
  else
    echo "📦 Creating new virtual environment in ./$VENV_DIR"
    python3 -m venv "$VENV_DIR"
  fi

  echo "⚙️ Activating virtual environment..."
  source "$VENV_DIR/bin/activate"
fi

# Check for requirements file and install if necessary
if [[ -f requirements.txt ]]; then
  echo "📜 Installing dependencies from requirements.txt..."
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "⚠️ No requirements.txt found. Skipping dependency installation."
fi

# Run the app
echo "🚀 Starting Python app..."
python3 app.py
