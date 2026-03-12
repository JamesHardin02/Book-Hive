from __future__ import annotations

from bookhive.db.models.book import Book
from bookhive.db.models.inventory import Inventory
from bookhive.services.settings_service import SettingsService
from sqlalchemy.orm import Session


class DashboardService:
    def __init__(self, db: Session, settings: SettingsService):
        self.db = db
        self.settings = settings

    def low_stock(self) -> dict:
        default_threshold = self.settings.get_low_stock_threshold()

        # Join Inventory -> Book for display
        rows = self.db.query(Inventory, Book).join(Book, Book.id == Inventory.book_id).all()

        low: list[dict] = []
        stockout: list[dict] = []

        for inv, book in rows:
            effective_threshold = (
                inv.min_threshold if inv.min_threshold is not None else default_threshold
            )
            item = {
                "book_id": book.id,
                "title": book.title,
                "isbn": book.isbn,
                "on_hand": inv.on_hand,
                "threshold": effective_threshold,
                "location": None
                if inv.location is None
                else {"aisle": inv.location.aisle, "shelf": inv.location.shelf},
            }

            if inv.on_hand == 0:
                stockout.append(item)
            elif inv.on_hand <= effective_threshold:
                low.append(item)

        # Sort ascending by on_hand for quick triage
        low.sort(key=lambda x: x["on_hand"])
        stockout.sort(key=lambda x: x["on_hand"])
        return {"default_threshold": default_threshold, "low_stock": low, "stockout": stockout}
