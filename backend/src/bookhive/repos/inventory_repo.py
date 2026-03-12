from __future__ import annotations

from bookhive.db.models.inventory import Inventory
from sqlalchemy.orm import Session


class InventoryRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_book_id(self, book_id: int) -> Inventory | None:
        return self.db.query(Inventory).filter(Inventory.book_id == book_id).first()

    def create_if_missing(self, *, book_id: int, on_hand: int = 0) -> Inventory:
        inv = self.get_by_book_id(book_id)
        if inv:
            return inv

        inv = Inventory(book_id=book_id, on_hand=on_hand, location_id=None)
        self.db.add(inv)
        self.db.commit()
        self.db.refresh(inv)
        return inv

    def set_on_hand(self, *, book_id: int, new_on_hand: int) -> Inventory:
        inv = self.create_if_missing(book_id=book_id, on_hand=0)
        inv.on_hand = new_on_hand
        self.db.commit()
        self.db.refresh(inv)
        return inv

    def set_location(self, *, book_id: int, location_id: int | None) -> Inventory:
        inv = self.create_if_missing(book_id=book_id, on_hand=0)
        inv.location_id = location_id
        self.db.commit()
        self.db.refresh(inv)
        return inv

    def set_min_threshold(self, *, book_id: int, min_threshold: int | None) -> Inventory:
        inv = self.create_if_missing(book_id=book_id, on_hand=0)
        inv.min_threshold = min_threshold
        self.db.commit()
        self.db.refresh(inv)
        return inv
