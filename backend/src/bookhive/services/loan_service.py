from __future__ import annotations

from datetime import date

from bookhive.db.models.loan import Loan
from bookhive.repos.book_repo import BookRepo
from bookhive.repos.inventory_repo import InventoryRepo
from bookhive.repos.loan_repo import LoanRepo
from bookhive.repos.member_repo import MemberRepo
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class LoanService:
    def __init__(
        self,
        db: Session,
        loan_repo: LoanRepo,
        book_repo: BookRepo,
        member_repo: MemberRepo,
        inventory_repo: InventoryRepo,
    ):
        self.db = db
        self.loan_repo = loan_repo
        self.book_repo = book_repo
        self.member_repo = member_repo
        self.inventory_repo = inventory_repo

    def create_loan(self, *, book_id: int, member_id: int, due_date: date) -> Loan:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        member = self.member_repo.get_by_id(member_id)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

        if due_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Due date cannot be in the past",
            )

        inventory = self.inventory_repo.get_by_book_id(book_id)
        if not inventory or inventory.on_hand <= 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Book is out of stock and cannot be checked out",
            )

        loan = Loan(
            book_id=book_id,
            member_id=member_id,
            created_at=date.today(),
            due_date=due_date,
            returned_at=None,
        )

        inventory.on_hand -= 1
        self.db.add(loan)
        self.db.commit()
        self.db.refresh(loan)
        return loan

    def list_loans(
        self,
        *,
        active_only: bool,
        overdue_only: bool,
        member_id: int | None,
        book_id: int | None,
        offset: int,
        limit: int,
    ) -> list[Loan]:
        return self.loan_repo.list_search(
            active_only=active_only,
            overdue_only=overdue_only,
            member_id=member_id,
            book_id=book_id,
            offset=offset,
            limit=limit,
        )

    def return_loan(self, *, loan_id: int) -> Loan:
        loan = self.loan_repo.get_by_id(loan_id)
        if not loan:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")

        if loan.returned_at is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Loan has already been returned",
            )

        inventory = self.inventory_repo.create_if_missing(book_id=loan.book_id, on_hand=0)

        loan.returned_at = date.today()
        inventory.on_hand += 1

        self.db.commit()
        self.db.refresh(loan)
        return loan
