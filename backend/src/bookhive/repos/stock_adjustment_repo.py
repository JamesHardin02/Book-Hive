from __future__ import annotations

from datetime import date

from bookhive.db.models.stock_adjustment import Stock_Adjustment
from sqlalchemy.orm import Session


class StockAdjustmentRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, book_id: int, user_id: int, delta: int, reason: str) -> Stock_Adjustment:
        row = Stock_Adjustment(
            book_id=book_id,
            user_id=user_id,
            delta=delta,
            reason=reason,
            created_at=date.today(),
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
