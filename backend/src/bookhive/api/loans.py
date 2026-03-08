from fastapi import APIRouter, Depends, Query

from bookhive.auth.dependencies import get_current_user
from bookhive.db.models.user import User
from bookhive.schemas.loans import LoanCreate, LoanOut
from bookhive.services.deps import get_loan_service
from bookhive.services.loan_service import LoanService

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("", response_model=LoanOut, status_code=201)
def create_loan(
    payload: LoanCreate,
    svc: LoanService = Depends(get_loan_service),
    _: User = Depends(get_current_user),
):
    return svc.create_loan(
        book_id=payload.book_id,
        member_id=payload.member_id,
        due_date=payload.due_date,
    )


@router.get("", response_model=list[LoanOut])
def list_loans(
    active_only: bool = True,
    overdue_only: bool = False,
    member_id: int | None = None,
    book_id: int | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    svc: LoanService = Depends(get_loan_service),
    _: User = Depends(get_current_user),
):
    return svc.list_loans(
        active_only=active_only,
        overdue_only=overdue_only,
        member_id=member_id,
        book_id=book_id,
        offset=offset,
        limit=limit,
    )


@router.patch("/{loan_id}/return", response_model=LoanOut)
def return_loan(
    loan_id: int,
    svc: LoanService = Depends(get_loan_service),
    _: User = Depends(get_current_user),
):
    return svc.return_loan(loan_id=loan_id)
