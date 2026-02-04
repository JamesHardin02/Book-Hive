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

## Configure env:

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

```
curl http://localhost:8000/health
```

- expected response should be the following

```
{"ok":true,"db":"connected"}
```
