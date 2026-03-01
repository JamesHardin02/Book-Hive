import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bookhive.api.admin import router as admin_router
from bookhive.api.auth import router as auth_router
from bookhive.api.health import router as health_router
from bookhive.db.init_db import init_db
from bookhive.observability.metrics import MetricsMiddleware
from bookhive.observability.metrics import router as metrics_router

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

app.add_middleware(MetricsMiddleware,)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(metrics_router)


@app.on_event("startup")
def on_startup() -> None:
    if os.getenv("BOOKHIVE_ENV") == "test":
        return
    init_db()
