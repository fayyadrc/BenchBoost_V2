#!/bin/zsh

# Activate the virtual environment
# This line sources the activate script from your .venv directory
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if activation was successful (optional, but good practice)
if [ $? -ne 0 ]; then
  echo "Failed to activate virtual environment. Exiting."
  exit 1
fi

