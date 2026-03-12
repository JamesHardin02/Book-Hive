from fastapi import APIRouter, Depends

from bookhive.auth.dependencies import get_current_user
from bookhive.db.models.user import User
from bookhive.services.dashboard_service import DashboardService
from bookhive.services.deps import get_dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/low-stock")
def low_stock(
    svc: DashboardService = Depends(get_dashboard_service),
    _: User = Depends(get_current_user),
):
    return svc.low_stock()
