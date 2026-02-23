#!/usr/bin/env bash
set -euo pipefail

# Always run from backend/ so:
# - python-dotenv loads backend/.env
# - --app-dir src resolves to backend/src
cd "$(dirname "$0")"

# Detect venv python path:
# - Windows Git Bash: .venv/Scripts/python.exe
# - macOS/Linux:      .venv/bin/python
if [[ -f ".venv/Scripts/python.exe" ]]; then
  VENV_PY="$(pwd)/.venv/Scripts/python.exe"
elif [[ -f ".venv/bin/python" ]]; then
  VENV_PY="$(pwd)/.venv/bin/python"
else
  echo "ERROR: Could not find venv python."
  echo "Create it with: cd backend && python -m venv .venv"
  exit 1
fi

"$VENV_PY" -m uvicorn bookhive.main:app \
  --reload \
  --host 0.0.0.0 \
  --port 8000 \
  --app-dir src
  