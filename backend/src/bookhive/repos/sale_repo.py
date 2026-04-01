from __future__ import annotations

from bookhive.db.models.sale import Sale
from sqlalchemy.orm import Session


class SaleRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sale_id: int) -> Sale | None:
        return self.db.query(Sale).filter(Sale.id == sale_id).first()

    def list_search(
        self,
        *,
        member_id: int | None,
        book_id: int | None,
        offset: int,
        limit: int,
    ) -> list[Sale]:
        qry = self.db.query(Sale)

        if member_id is not None:
            qry = qry.filter(Sale.member_id == member_id)

        if book_id is not None:
            qry = qry.filter(Sale.book_id == book_id)

        return qry.order_by(Sale.sold_at.desc(), Sale.id.desc()).offset(offset).limit(limit).all()
