from __future__ import annotations

from bookhive.repos.inventory_repo import InventoryRepo
from bookhive.repos.location_repo import LocationRepo
from bookhive.repos.stock_adjustment_repo import StockAdjustmentRepo
from fastapi import HTTPException


class InventoryService:
    def __init__(
        self,
        inv_repo: InventoryRepo,
        loc_repo: LocationRepo,
        adj_repo: StockAdjustmentRepo,
    ):
        self.inv_repo = inv_repo
        self.loc_repo = loc_repo
        self.adj_repo = adj_repo

    def adjust_stock(self, *, book_id: int, user_id: int, delta: int, reason: str):
        inv = self.inv_repo.create_if_missing(book_id=book_id, on_hand=0)
        new_on_hand = inv.on_hand + delta
        if new_on_hand < 0:
            raise HTTPException(status_code=400, detail="Stock cannot go below zero")

        inv = self.inv_repo.set_on_hand(book_id=book_id, new_on_hand=new_on_hand)
        self.adj_repo.create(book_id=book_id, user_id=user_id, delta=delta, reason=reason)
        return inv

    def set_location(self, *, book_id: int, aisle: str, shelf: str):
        loc = self.loc_repo.get_or_create(aisle=aisle, shelf=shelf)
        return self.inv_repo.set_location(book_id=book_id, location_id=loc.id)

    def set_min_threshold(self, *, book_id: int, min_threshold: int | None):
        return self.inv_repo.set_min_threshold(book_id=book_id, min_threshold=min_threshold)
