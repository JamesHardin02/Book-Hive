from __future__ import annotations

from datetime import date
from decimal import Decimal

from bookhive.db.models.sale import Sale
from bookhive.repos.book_repo import BookRepo
from bookhive.repos.inventory_repo import InventoryRepo
from bookhive.repos.member_repo import MemberRepo
from bookhive.repos.sale_repo import SaleRepo
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class SaleService:
    def __init__(
        self,
        db: Session,
        sale_repo: SaleRepo,
        book_repo: BookRepo,
        member_repo: MemberRepo,
        inventory_repo: InventoryRepo,
    ):
        self.db = db
        self.sale_repo = sale_repo
        self.book_repo = book_repo
        self.member_repo = member_repo
        self.inventory_repo = inventory_repo

    def create_sale(
        self,
        *,
        book_id: int,
        member_id: int | None,
        quantity: int,
        unit_price: Decimal,
    ) -> Sale:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

        member = None
        if member_id is not None:
            member = self.member_repo.get_by_id(member_id)
            if not member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Member not found"
                )

        inventory = self.inventory_repo.get_by_book_id(book_id)
        if not inventory or inventory.on_hand < quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Not enough stock to complete sale",
            )

        sale = Sale(
            book_id=book_id,
            member_id=None if member is None else member.id,
            quantity=quantity,
            unit_price=unit_price,
            sold_at=date.today(),
        )

        inventory.on_hand -= quantity
        self.db.add(sale)
        self.db.commit()
        self.db.refresh(sale)
        return sale

    def list_sales(
        self,
        *,
        member_id: int | None,
        book_id: int | None,
        offset: int,
        limit: int,
    ) -> list[Sale]:
        return self.sale_repo.list_search(
            member_id=member_id,
            book_id=book_id,
            offset=offset,
            limit=limit,
        )
