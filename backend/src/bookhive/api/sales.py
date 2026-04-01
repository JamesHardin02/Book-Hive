from fastapi import APIRouter, Depends, Query

from bookhive.auth.dependencies import get_current_user
from bookhive.db.models.user import User
from bookhive.schemas.sales import SaleCreate, SaleOut
from bookhive.services.deps import get_sale_service
from bookhive.services.sale_service import SaleService

router = APIRouter(prefix="/sales", tags=["sales"])


@router.post("", response_model=SaleOut, status_code=201)
def create_sale(
    payload: SaleCreate,
    svc: SaleService = Depends(get_sale_service),
    _: User = Depends(get_current_user),
):
    return svc.create_sale(
        book_id=payload.book_id,
        member_id=payload.member_id,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
    )


@router.get("", response_model=list[SaleOut])
def list_sales(
    member_id: int | None = None,
    book_id: int | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    svc: SaleService = Depends(get_sale_service),
    _: User = Depends(get_current_user),
):
    return svc.list_sales(
        member_id=member_id,
        book_id=book_id,
        offset=offset,
        limit=limit,
    )
