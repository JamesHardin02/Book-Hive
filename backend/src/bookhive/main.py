from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bookhive.api.auth import router as auth_router
from bookhive.api.health import router as health_router
from bookhive.db.init_db import init_db

app = FastAPI(title="BookHive API")

# CORS: allow the frontend dev server to call the backend in development
# Vite default: http://localhost:5173
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)

@app.on_event("startup")
def on_startup() -> None:
    init_db()
