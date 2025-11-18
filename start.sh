#!/bin/bash

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

# Run as a module so relative imports work
python3 -m src.main

if [ $? -ne 0 ]; then
  echo "Application failed. Exiting."
  exit 1
fi
