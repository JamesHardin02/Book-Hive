from fastapi import FastAPI

from bookhive.api.health import router as health_router

app = FastAPI(title="BookHive API")
app.include_router(health_router)
