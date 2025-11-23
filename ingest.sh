#!/usr/bin/env zsh
# BenchBoost data ingestion helper
# Usage examples:
#   ./ingest.sh bootstrap              # players/teams/gameweeks
#   ./ingest.sh fixtures               # all fixtures
#   ./ingest.sh event 15               # player GW stats for event 15
#   ./ingest.sh manager 1605977        # manager summary/history/transfers
#   ./ingest.sh manager 1605977 15     # + picks for event 15
#   ./ingest.sh full                   # bootstrap + fixtures
#   ./ingest.sh manager-full 1605977 15  # full + manager + picks
#
# Ensure you have a .env with MONGO_URI and MONGO_DB_NAME if not default.

set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

# 1. Load .env if present
if [ -f .env ]; then
  echo "Loading .env..."
  sanitized_env=$(mktemp)
  awk -F= '/^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=/ {
    key=$1; sub(/^[[:space:]]*/,"",key); sub(/[[:space:]]*/,"",key);
    val=$2; for(i=3;i<=NF;i++){val=val"="$i}
    sub(/^[[:space:]]*/,"",val); sub(/[[:space:]]*$/,"",val);
    if (val ~ /^".*"$/) { sub(/^"/,"",val); sub(/"$/,"",val); }
    if (val ~ /^'\''.*'\''$/) { sub(/^'\''/,"",val); sub(/'\''$/,"",val); }
    print key"="val
  }' .env > "$sanitized_env"
  set -a; source "$sanitized_env" || echo "Warning: could not source .env"; set +a
  rm -f "$sanitized_env"
fi

# 2. Activate virtual environment
if [ ! -f .venv/bin/activate ]; then
  echo "Error: .venv missing. Create with: python3 -m venv .venv" >&2
  exit 1
fi
source .venv/bin/activate

# 3. Ensure dependencies installed (only once)
if ! python -c 'import pymongo' >/dev/null 2>&1; then
  if [ -f requirements.txt ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
  else
    echo "requirements.txt missing" >&2
    exit 1
  fi
fi

# 4. Ensure indexes
python backend/database/mongo.py >/dev/null || echo "Index creation completed (or already exists)."

ACTION=${1:-}
if [ -z "$ACTION" ]; then
  echo "No action provided. See header for usage." >&2
  exit 1
fi

shift || true
EVENT=""  # optional
ENTRY=""  # optional
PICKS="false"

# Helper to build python command
run_ingest() {
  echo "Running: $*"
  python backend/database/ingest.py "$@"
}

case "$ACTION" in
  bootstrap)
    run_ingest bootstrap
    ;;
  fixtures)
    run_ingest fixtures
    ;;
  event)
    EVENT=${1:-}
    if [ -z "$EVENT" ]; then echo "event id required" >&2; exit 1; fi
    run_ingest event --event "$EVENT"
    ;;
  full)
    run_ingest full
    ;;
  manager)
    ENTRY=${1:-}
    EVENT=${2:-}
    if [ -z "$ENTRY" ]; then echo "entry id required" >&2; exit 1; fi
    if [ -n "$EVENT" ]; then
      run_ingest bootstrap --manager --entry "$ENTRY" --event "$EVENT"
    else
      run_ingest bootstrap --manager --entry "$ENTRY"
    fi
    ;;
  manager-full)
    ENTRY=${1:-}
    EVENT=${2:-}
    if [ -z "$ENTRY" ]; then echo "entry id required" >&2; exit 1; fi
    if [ -z "$EVENT" ]; then echo "event id required for manager-full" >&2; exit 1; fi
    run_ingest full --manager --entry "$ENTRY" --event "$EVENT"
    ;;
  *)
    echo "Unknown action: $ACTION" >&2
    exit 1
    ;;
 esac

 echo "Ingestion action '$ACTION' complete."