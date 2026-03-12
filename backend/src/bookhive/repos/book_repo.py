from __future__ import annotations

from bookhive.db.models.book import Book
from sqlalchemy.orm import Session


class BookRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, book_id: int) -> Book | None:
        return self.db.query(Book).filter(Book.id == book_id).first()

    def get_by_isbn_edition(self, isbn: str, edition: int) -> Book | None:
        return self.db.query(Book).filter(Book.isbn == isbn).filter(Book.edition == edition).first()

    def max_edition_for_isbn(self, isbn: str) -> int | None:
        row = (
            self.db.query(Book.edition)
            .filter(Book.isbn == isbn)
            .order_by(Book.edition.desc())
            .first()
        )
        return None if row is None else int(row[0])

    def create(self, book: Book) -> Book:
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def delete(self, book: Book) -> None:
        self.db.delete(book)
        self.db.commit()

    def list_search(
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
        qry = self.db.query(Book)

        if q:
            like = f"%{q}%"
            qry = qry.filter(
                (Book.title.ilike(like))
                | (Book.author.ilike(like))
                | (Book.genre.ilike(like))
                | (Book.isbn.ilike(like))
            )
        if title:
            qry = qry.filter(Book.title.ilike(f"%{title}%"))
        if author:
            qry = qry.filter(Book.author.ilike(f"%{author}%"))
        if isbn:
            qry = qry.filter(Book.isbn.ilike(f"%{isbn}%"))
        if genre:
            qry = qry.filter(Book.genre.ilike(f"%{genre}%"))
        if year_min is not None:
            qry = qry.filter(Book.year >= year_min)
        if year_max is not None:
            qry = qry.filter(Book.year <= year_max)

        return qry.order_by(Book.title.asc()).offset(offset).limit(limit).all()
