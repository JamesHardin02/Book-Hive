from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from bookhive.db.models.metadata_cache import Metadata_Cache
from sqlalchemy.orm import Session


class MetadataCacheRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_fresh_payload(self, *, isbn: str, max_age_hours: int = 24) -> dict | None:
        row = self.db.query(Metadata_Cache).filter(Metadata_Cache.isbn == isbn).first()
        if not row:
            return None

        now = datetime.now(timezone.utc)  # noqa: UP017
        if row.fetched_at.tzinfo is None:
            # If DB stored naive, treat as UTC
            fetched = row.fetched_at.replace(tzinfo=timezone.utc)  # noqa: UP017
        else:
            fetched = row.fetched_at

        if now - fetched > timedelta(hours=max_age_hours):
            return None

        return json.loads(row.payload)

    def upsert(self, *, isbn: str, payload: dict) -> None:
        s = json.dumps(payload, ensure_ascii=False)
        row = self.db.query(Metadata_Cache).filter(Metadata_Cache.isbn == isbn).first()
        if row:
            row.payload = s
            row.fetched_at = datetime.now(timezone.utc)  # noqa: UP017
        else:
            row = Metadata_Cache(isbn=isbn, payload=s, fetched_at=datetime.now(timezone.utc))  # noqa: UP017
            self.db.add(row)

        self.db.commit()
