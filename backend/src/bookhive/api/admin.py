from fastapi import APIRouter, Depends

from bookhive.auth.dependencies import require_admin_user
from bookhive.db.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ping")
def admin_ping(current_user: User = Depends(require_admin_user)):
    return {"ok": True, "user_id": current_user.id}
