# root directory setup

```
npm install
```

# backend directory setup

```
cd backend
py -3.13 -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

# Database setup (from root directory)

```
docker compose up -d
```

# run backend server

```
python -m uvicorn bookhive.main:app --reload --app-dir --port 8000
```
