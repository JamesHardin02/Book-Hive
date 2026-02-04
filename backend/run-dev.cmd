@echo off
REM Run FastAPI dev server using the venv Python (no manual activation needed)

setlocal

REM Always run from backend/ so:
REM - python-dotenv loads backend/.env
REM - --app-dir src resolves to backend/src
cd /d "%~dp0"

set "PY=%CD%\.venv\Scripts\python.exe"

IF NOT EXIST "%PY%" (
  echo ERROR: Could not find venv python at "%PY%"
  echo Create it with: cd backend ^&^& py -3.13 -m venv .venv
  exit /b 1
)

"%PY%" -m uvicorn bookhive.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src
