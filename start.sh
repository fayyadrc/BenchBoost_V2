#!/bin/zsh

echo "Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
  if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment. Exiting."
    exit 1
  fi
else
  echo ".venv not found; continuing without virtual environment"
fi


# Change to the parent of the script's directory so the package folder
# (named `fplAI`) is on Python's import path, then run the app.
cd "$(dirname "$0")/.." || { echo "Failed to change directory to project parent"; exit 1; }

# Run as a module so relative imports work
python3 -m fplAI.src.main

if [ $? -ne 0 ]; then
  echo "Application failed. Exiting."
  exit 1
fi