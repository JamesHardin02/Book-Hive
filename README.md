# BookHive (CSC.289 Capstone)

BookHive is a manager-only web app that helps bookstore and library managers manage inventory, circulation (loans/returns), manual sales, and operational insights through dashboards.

This is a Wake Tech **CSC.289 Programming Capstone** project built by Team 1 for Spring 2026.

## Tech stack

- **Frontend:** Vue 3 + Vite + Pinia + Vue Router
- **Backend:** Python 3.13 + FastAPI
- **Database:** MySQL (Docker) + SQLAlchemy + mysqlclient
- **Auth:** OAuth2 Password Flow + JWT + bcrypt
- **CI:** GitHub Actions (Super-Linter + Ruff + ESLint/Prettier)
- **Project management:** Trello (Scrum/Kanban), MS Teams (communication)

## Repo structure

- `frontend/` — Vue single-page application
- `backend/` — FastAPI backend (`backend/src/bookhive`)
- `docs/` — developer documentation and workflows
- `.github/` — CI, templates, CODEOWNERS, dependabot

## Quickstart (local development)

### Prereqs

- Node.js (see `frontend/package.json` engines)
- Python 3.13
- Docker Desktop

### 1) Install root tools (formatting + orchestrated dev)

```bash
npm install
```

### 2) Start database

```bash
docker compose up -d
docker ps
```

#### (Optional) Check successful DB table creation through MySQL CLI
```bash
mysql -u root -p -h 127.0.0.1 -P 3307
USE bookhive;
SELECT DATABASE();
SHOW DATABASES;
SHOW TABLES;
```

### 3) Backend setup

```bash
cd backend
py -3.13 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Copy env config

```bash
cp .env.example .env
```

#### Run backend

```bash
cd ..
npm run dev:backend
```

### 4) Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 5) Run both from repo root

```bash
cd ..
npm run dev
```

## Validate services

### Backend DB connectivity

```bash
curl http://localhost:8000/health
```

### Expected

```json
{ "ok": true, "db": "connected" }
```

## Formatting & Linting

### Repo-wide formatting

```bash
npm run format
```

### Backend lint/format

```bash
cd backend
source .venv/Scripts/activate
ruff check .
ruff format .
```

### Frontend lint/format

```bash
cd frontend
npm run lint
npm run format
```

## Test

### Backend unit tests

```bash
cd backend
source .venv/Scripts/activate
python -m unittest discover -s tests -p "test_*.py" -v
```

### Frontend unit tesxts

```bash
cd frontend
npm run test:unit
```

## Workflow & Contribution

See the following

- `CONTRIBUTING.md` - How to branch, commit, open PRs, run checks
- `docs/WORKFLOW.md` - sprint branching strategy and merge rules
