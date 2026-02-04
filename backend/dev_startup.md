## Local Development (Backend)

### Prereqs

- Python 3.13
- Docker Desktop

### Setup

1. Start MySQL:
   - `docker compose up -d`

2. Create/activate venv and install deps:
   - `cd backend`
   - `py -3.13 -m venv .venv`
   - `source .venv/Scripts/activate`
   - `pip install -r requirements.txt`
   - `pip install -r requirements-dev.txt`

3. Configure env:
   - Copy `backend/.env.example` to `backend/.env`; keep values for local dev db connection.

4. Run API:
   - `python -m uvicorn bookhive.main:app --reload --host 0.0.0.0 --port 8000 --app-dir src`

5. Verify:
   - `curl http://localhost:8000/health`
