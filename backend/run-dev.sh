#!/usr/bin/env bash
set -euo pipefail

# Always run from backend/ so:
# - --app-dir src points to backend/src
# - python-dotenv loads backend/.env
cd "$(dirname "$0")"

VENV_PY="$(pwd)/.venv/Scripts/python.exe"

if [[ ! -f "$VENV_PY" ]]; then
  echo "ERROR: Could not find venv python at: $VENV_PY"
  echo "Create it with: cd backend && py -3.13 -m venv .venv"
  exit 1
fi

"$VENV_PY" -m uvicorn bookhive.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000 \
  --app-dir src
