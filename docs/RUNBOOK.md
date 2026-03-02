# BookHive Runbook (Local Dev + Troubleshooting)

This runbook is a quick-reference for running BookHive locally and diagnosing common issues.

## Quick commands

### Start database (MySQL)

```bash
docker compose up -d
docker ps
```

### Start both frontend + backend (root)

```bash
npm install
npm run dev
```

### Start backend only

```bash
cd backend
# Windows
backend\run-dev.cmd
# macOS/Linux
bash ./run-dev.sh
```

### Start frontend only

```bash
cd frontend
npm install
npm run dev
```

### Seed demo data

```bash
python scripts/seed_db.py --reset
python scripts/seed_db.py
```

#### Verify via MySQL CLI

```bash
mysql -u root -p -h 127.0.0.1 -P 3307
USE bookhive;
SHOW TABLES;
SELECT * FROM user;
SELECT * FROM book;
SELECT * FROM loan;
```

### Run tests

#### from repo root

```bash
npm run test
```

#### Backend only

```bash
cd backend
python -m unittest discover -s tests -p "test_*.py" -v
```

#### Frontend only

```bash
cd frontend
npm run test:unit
```

### Common issues

1. Backend health check fails (/health shows db error)

#### Symptoms

- `curl http://localhost:8000/health`
- /health returns `{ ok: false, db: "error: ..." }`

#### Fix

- Ensure MySQL container is running the following

```bash
docker ps
docker compose up -d
```

- Ensure the port matches your env (DB_PORT=3307 is the default in the code)

2. Port already in use

#### MySQL port 3307 already used

- Change docker-compose.yml host port or stop the conflicting service.

#### Backend port 8000 already used

- Stop the other process or run uvicorn on a different port

3. Login fails with 401 (incorrect credentials)

- Seeded admin user (if seeded)
- - email: `manager@example.com`
- - password: `manager123`
- Note: /auth/token uses OAuth2PasswordRequestForm and the frontend sends email via the username field.

4. CORS errors in the browser console

- Ensure frontend origin is included in backend CORS list (http://localhost:5173)
- Ensure VITE_API_BASE_URL points to the correct backend URL.

5. Register fails due to email validation

- If EMAIL_MX_CHECK is enabled, domain without valid MX records may fail.
- For tests/CI this should be disabled to avoid DNS failure.

6. "trapped error reading bcrypt version"

- This is a noisy passlib/bcrupt logging issue in some environments.
- Suppress passlib bcrypt logging in seed/tests.
- If auth hashing fails, reinstall dependencies

```bash
pip install -r backend/requirements.txt
```

7. Operational notes (MVP)

- Tokens are stored in `localStorage` for MVP
- In a production deployment, use HttpOnly cookies or a more secure storage strategy.
