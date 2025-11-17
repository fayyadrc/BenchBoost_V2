#!/bin/zsh

echo "Activating virtual environment..."
source .venv/bin/activate

# Run main.py from the parent directory
cd 
python3 fplAI/main.py

if [ $? -ne 0 ]; then
  echo "Failed to activate virtual environment. Exiting."
  exit 1
fi