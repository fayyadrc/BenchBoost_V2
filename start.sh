#!/bin/bash

set -u

FRONTEND_PID=""

cleanup() {
  if [ -n "${FRONTEND_PID}" ] && ps -p "${FRONTEND_PID}" > /dev/null 2>&1; then
    echo "Stopping frontend dev server (PID: ${FRONTEND_PID})..."
    kill "${FRONTEND_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT INT TERM

echo "Loading .env if present..."
if [ -f ".env" ]; then
  # export all variables loaded from .env
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
  echo ".env loaded."
else
  echo "No .env file found. Proceeding with current environment."
fi

# Ensure a Python virtual environment exists
if [ ! -f ".venv/bin/activate" ]; then
  echo "Creating Python virtual environment (.venv)..."
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv .venv || {
      echo "Failed to create venv with python3; trying python..."
      python -m venv .venv || {
        echo "Could not create virtual environment. Please install Python 3."; exit 1; }
    }
  else
    echo "python3 not found. Please install Python 3."; exit 1
  fi
fi

# Default FRONTEND_URLS for local dev if not set
if [ -z "${FRONTEND_URLS:-}" ]; then
  export FRONTEND_URLS="http://localhost:5173"
  echo "FRONTEND_URLS not set. Defaulting to ${FRONTEND_URLS} for local dev."
fi

# Helpful warning for missing API keys used by the agent
if [ -z "${GOOGLE_API_KEY:-}" ]; then
  echo "Warning: GOOGLE_API_KEY is not set. The agent may fail to respond."
fi

echo "Starting frontend dev server..."
if [ -d "frontend" ]; then
  pushd frontend > /dev/null
  if command -v npm >/dev/null 2>&1; then
    if [ ! -d node_modules ]; then
      echo "Installing frontend dependencies..."
      npm install || { echo "npm install failed"; exit 1; }
    fi
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend started (PID: $FRONTEND_PID)."
  else
    echo "npm not found; skipping frontend start."
  fi
  popd > /dev/null
else
  echo "frontend/ directory not found; skipping frontend start."
fi

echo "Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
  if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment. Exiting."
    exit 1
  fi
else
  echo ".venv not found; continuing without virtual environment"
fi

echo "Checking Python dependencies..."
python - <<'PY' 2>/dev/null
try:
    import fastapi, uvicorn, langchain_core, langchain_google_genai  # noqa: F401
    print('OK')
except Exception:
    print('MISSING')
PY
if [ "$(python - <<'PY'
try:
    import fastapi, uvicorn, langchain_core, langchain_google_genai
    print('OK')
except Exception:
    print('MISSING')
PY
)" != "OK" ]; then
  echo "Installing Python dependencies from requirements.txt..."
  if [ -f requirements.txt ]; then
    pip install -r requirements.txt || { echo "pip install failed"; exit 1; }
  else
    echo "requirements.txt not found. Please install dependencies manually."; exit 1
  fi
fi

echo "Starting FastAPI backend with Uvicorn..."
# Ensure uvicorn is importable in the active Python environment
python -c 'import uvicorn' >/dev/null 2>&1 || { echo "uvicorn not installed in the active environment"; exit 1; }

# Use PORT env var if provided, else default to 8000
PORT=${PORT:-8000}

python -m uvicorn backend.middleware.api:app --reload --host 0.0.0.0 --port "$PORT"

STATUS=$?
if [ $STATUS -ne 0 ]; then
  echo "Backend failed with status $STATUS. Exiting."
  exit $STATUS
fi

