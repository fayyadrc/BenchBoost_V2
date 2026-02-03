#!/usr/bin/env zsh

set -euo pipefail

echo "=== BenchBoost Dev Starter ==="

# 1. Load environment variables if .env exists (robust parsing)
if [ -f .env ]; then
  echo "Loading .env..."
  # Create a sanitized temp version supporting whitespace around '='
  sanitized_env=$(mktemp)
  # Keep only KEY=VALUE lines, strip surrounding spaces, remove inline comments
  awk -F= '/^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=/ {
    key=$1; sub(/^[[:space:]]*/,"",key); sub(/[[:space:]]*/,"",key);
    val=$2; for(i=3;i<=NF;i++){val=val"="$i} # Rejoin if value had '='
    sub(/^[[:space:]]*/,"",val); sub(/[[:space:]]*$/,"",val);
    # Remove surrounding quotes
    if (val ~ /^".*"$/) { sub(/^"/,"",val); sub(/"$/,"",val); }
    if (val ~ /^'\''.*'\''$/) { sub(/^'\''/,"",val); sub(/'\''$/,"",val); }
    print key"="val
  }' .env > "$sanitized_env"
  set -a
  # shellcheck disable=SC1090
  source "$sanitized_env" || echo "Warning: failed to source sanitized .env"
  set +a
  rm -f "$sanitized_env"
  echo ".env loaded."
else
  echo "No .env file found (continuing)."
fi

# 2. Activate existing virtual environment (required by user spec)
if [ ! -f .venv/bin/activate ]; then
  echo "Error: .venv does not exist. Create it with: python3 -m venv .venv" >&2
  exit 1
fi
source .venv/bin/activate
echo "Activated Python virtual environment (.venv)."

# 3. Ensure backend Python deps are installed (FastAPI + Uvicorn for API, LangChain for agent)
if ! python -c 'import fastapi, uvicorn, langchain' >/dev/null 2>&1; then
  if [ -f requirements.txt ]; then
    echo "Installing backend Python dependencies..."
    pip install -r requirements.txt
  else
    echo "requirements.txt missing; cannot auto-install dependencies." >&2
    exit 1
  fi
fi

# 4. Start FastAPI backend API (proxied by Vite) in background
PORT=${PORT:-8000}
echo "Starting backend API on port ${PORT}..."
# Use the new unified entry point (backend.main)
# UVICORN_RELOAD=true enables auto-reload during development
UVICORN_RELOAD=true python -m backend.main &
BACKEND_PID=$!
echo "Backend PID: ${BACKEND_PID}"

# 5. Start frontend (Vite) dev server
if [ ! -d frontend ]; then
  echo "Error: frontend directory missing." >&2
  kill ${BACKEND_PID} 2>/dev/null || true
  exit 1
fi
pushd frontend >/dev/null
if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm not found. Install Node.js." >&2
  popd >/dev/null
  kill ${BACKEND_PID} 2>/dev/null || true
  exit 1
fi
if [ ! -d node_modules ]; then
  echo "Installing frontend dependencies..."
  npm install
fi
echo "Starting Vite dev server (frontend)..."
npm run dev &
FRONTEND_PID=$!
popd >/dev/null
echo "Frontend PID: ${FRONTEND_PID}"

# 6. Trap cleanup so both processes stop together
cleanup() {
  echo "\nShutting down..."
  kill ${BACKEND_PID} 2>/dev/null || true
  kill ${FRONTEND_PID} 2>/dev/null || true
}
trap cleanup INT TERM EXIT

echo "\nBackend: http://localhost:${PORT} (API endpoints)"
echo "Frontend: http://localhost:5173 (proxied /api -> backend)"
echo "Press Ctrl+C to stop both."

# 7. Wait on both (first to exit triggers cleanup)
wait

