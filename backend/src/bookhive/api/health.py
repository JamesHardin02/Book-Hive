from fastapi import APIRouter
from bookhive.db.engine import db_healthcheck

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
def health():
    ok, detail = db_healthcheck()
    return {"ok": ok, "db": detail}
