from __future__ import annotations

from bookhive.db.models.book import Book
from bookhive.repos.book_repo import BookRepo
from bookhive.repos.inventory_repo import InventoryRepo
from bookhive.repos.location_repo import LocationRepo
from fastapi import HTTPException, status


class BookService:
    def __init__(self, book_repo: BookRepo, inv_repo: InventoryRepo, loc_repo: LocationRepo):
        self.book_repo = book_repo
        self.inv_repo = inv_repo
        self.loc_repo = loc_repo

    def create_book(
        self,
        *,
        isbn: str,
        title: str,
        author: str,
        genre: str,
        year: int,
        unit_price,
        cover_url,
        initial_on_hand: int,
        location: dict | None,
        allow_new_edition: bool,
        edition: int | None,
    ) -> Book:
        # Decide edition:
        if edition is None:
            edition = 1

        existing = self.book_repo.get_by_isbn_edition(isbn, edition)
        if existing:
            if allow_new_edition and edition == 1:
                max_ed = self.book_repo.max_edition_for_isbn(isbn) or 1
                edition = max_ed + 1
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A book with this ISBN and edition already exists",
                )

        book = Book(
            isbn=isbn,
            edition=edition,
            title=title,
            author=author,
            genre=genre,
            year=year,
            unit_price=unit_price,
            cover_url=cover_url,
        )
        book = self.book_repo.create(book)

        # Create inventory row
        inv = self.inv_repo.create_if_missing(book_id=book.id, on_hand=initial_on_hand)

        # Assign location if provided
        if location is not None:
            loc = self.loc_repo.get_or_create(aisle=location["aisle"], shelf=location["shelf"])
            self.inv_repo.set_location(book_id=book.id, location_id=loc.id)

        # Refresh relationship on book
        _ = inv
        return self.book_repo.get_by_id(book.id) or book

    def update_book(self, *, book_id: int, **fields) -> Book:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        for k, v in fields.items():
            if v is not None:
                setattr(book, k, v)

        self.book_repo.db.commit()
        self.book_repo.db.refresh(book)
        return book

    def delete_book(self, *, book_id: int) -> None:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        self.book_repo.delete(book)

    def get_book(self, *, book_id: int) -> Book:
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

    def search(
        self,
        *,
        q: str | None,
        title: str | None,
        author: str | None,
        isbn: str | None,
        genre: str | None,
        year_min: int | None,
        year_max: int | None,
        offset: int,
        limit: int,
    ) -> list[Book]:
        return self.book_repo.list_search(
            q=q,
            title=title,
            author=author,
            isbn=isbn,
            genre=genre,
            year_min=year_min,
            year_max=year_max,
            offset=offset,
            limit=limit,
        )
