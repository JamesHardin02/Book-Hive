from fastapi import APIRouter, Depends

from bookhive.auth.dependencies import get_current_user
from bookhive.db.models.user import User
from bookhive.schemas.settings import LowStockThresholdIn, LowStockThresholdOut
from bookhive.services.deps import get_settings_service
from bookhive.services.settings_service import SettingsService

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/low-stock-threshold", response_model=LowStockThresholdOut)
def get_threshold(
    svc: SettingsService = Depends(get_settings_service),
    _: User = Depends(get_current_user),
):
    return {"threshold": svc.get_low_stock_threshold()}


@router.put("/low-stock-threshold", response_model=LowStockThresholdOut)
def set_threshold(
    payload: LowStockThresholdIn,
    svc: SettingsService = Depends(get_settings_service),
    _: User = Depends(get_current_user),
):
    svc.set_low_stock_threshold(payload.threshold)
    return {"threshold": svc.get_low_stock_threshold()}
