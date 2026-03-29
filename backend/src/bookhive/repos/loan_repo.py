from __future__ import annotations

from datetime import date, timedelta

from bookhive.db.models.loan import Loan
from sqlalchemy.orm import Session


class LoanRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, loan_id: int) -> Loan | None:
        return self.db.query(Loan).filter(Loan.id == loan_id).first()

    def list_search(
        self,
        *,
        active_only: bool,
        overdue_only: bool,
        due_soon_only: bool,
        due_within_days: int,
        member_id: int | None,
        book_id: int | None,
        offset: int,
        limit: int,
    ) -> list[Loan]:
        qry = self.db.query(Loan)
        today = date.today()

        if active_only:
            qry = qry.filter(Loan.returned_at.is_(None))

        if overdue_only:
            qry = qry.filter(Loan.returned_at.is_(None)).filter(Loan.due_date < today)

        if due_soon_only:
            due_soon_end = today + timedelta(days=due_within_days)
            qry = qry.filter(Loan.returned_at.is_(None))
            qry = qry.filter(Loan.due_date >= today).filter(Loan.due_date <= due_soon_end)

        if member_id is not None:
            qry = qry.filter(Loan.member_id == member_id)

        if book_id is not None:
            qry = qry.filter(Loan.book_id == book_id)

        return qry.order_by(Loan.due_date.asc(), Loan.id.desc()).offset(offset).limit(limit).all()
