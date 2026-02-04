# Dev setup

## root directory setup

```bash
npm install
```

## backend directory setup

```bash
cd backend
py -3.13 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Configure env

- Copy `backend/.env.example` to `backend/.env`; keep values for local dev db connection.

## Database setup (from root directory)

```bash
docker compose up -d
```

## run backend server

```bash
cd backend
source .venv/Scripts/activate
python -m uvicorn bookhive.main:app --reload --app-dir src --port 8000
```

## test DB connection

- In a new terminal after set up the server execute the following

```bash
curl http://localhost:8000/health
```

- expected response should be the following

```bash
{"ok":true,"db":"connected"}
```

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

- npm run dev will start both the backend server and the frontend
- The backend needs to be running for /ApiStatus to pass confirmation test to the database
- default Windows .cmd file launches backend via npm run dev. Switch concurrently backend launch command to dev:backend:bash if developing on MacOS/Unix/Linux systems
