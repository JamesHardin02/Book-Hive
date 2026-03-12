from __future__ import annotations

from bookhive.db.models.location import Location
from sqlalchemy.orm import Session


class LocationRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, location_id: int) -> Location | None:
        return self.db.query(Location).filter(Location.id == location_id).first()

    def get_by_aisle_shelf(self, aisle: str, shelf: str) -> Location | None:
        return (
            self.db.query(Location)
            .filter(Location.aisle == aisle)
            .filter(Location.shelf == shelf)
            .first()
        )

    def get_or_create(self, *, aisle: str, shelf: str) -> Location:
        existing = self.get_by_aisle_shelf(aisle, shelf)
        if existing:
            return existing

        loc = Location(aisle=aisle, shelf=shelf)
        self.db.add(loc)
        self.db.commit()
        self.db.refresh(loc)
        return loc

    def list_all(self) -> list[Location]:
        return self.db.query(Location).order_by(Location.aisle.asc(), Location.shelf.asc()).all()
