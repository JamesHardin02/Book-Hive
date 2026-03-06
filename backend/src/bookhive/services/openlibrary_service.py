from __future__ import annotations

import httpx
from bookhive.repos.metadata_cache_repo import MetadataCacheRepo


class OpenLibraryService:
    def __init__(self, cache_repo: MetadataCacheRepo):
        self.cache_repo = cache_repo

    def lookup_isbn(self, isbn: str) -> dict:
        cached = self.cache_repo.get_fresh_payload(isbn=isbn, max_age_hours=24)
        if cached is not None:
            return cached

        url = "https://openlibrary.org/api/books"
        params = {
            "bibkeys": f"ISBN:{isbn}",
            "format": "json",
            "jscmd": "data",
        }

        # Requirement: timeout <= 3 seconds
        with httpx.Client(timeout=3.0) as client:
            res = client.get(url, params=params)

        res.raise_for_status()
        data = res.json()

        key = f"ISBN:{isbn}"
        payload = data.get(key)
        if payload is None:
            # let API layer convert this to 404.
            return {}

        normalized = {
            "isbn": isbn,
            "title": payload.get("title"),
            "authors": [a.get("name") for a in payload.get("authors", []) if a.get("name")],
            "publish_year": payload.get("publish_date"),
            "cover_url": (payload.get("cover") or {}).get("large")
            or (payload.get("cover") or {}).get("medium")
            or (payload.get("cover") or {}).get("small"),
        }

        # publish_date is often a string like "2001" or "Oct 2001"
        # Keep parsing simple for MVP: if it starts with digits, try int
        py = normalized["publish_year"]
        if isinstance(py, str):
            digits = "".join(ch for ch in py if ch.isdigit())
            normalized["publish_year"] = int(digits[:4]) if len(digits) >= 4 else None

        self.cache_repo.upsert(isbn=isbn, payload=normalized)
        return normalized
