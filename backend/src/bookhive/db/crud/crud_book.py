from typing import list

from bookhive.crud import crud_book  # the CRUD file we just made
from bookhive.db.engine import get_db  # function to provide SQLAlchemy session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/books", tags=["books"])


# -----------------------------
# CREATE
# -----------------------------
@router.post("", response_model=dict)
def create_book(
    isbn: str,
    title: str,
    author: str,
    genre: str,
    year: int,
    unit_price: float | None,
    cover_url: str | None,
    db: Session = Depends(get_db),
):
    book = crud_book.create_book(
        db=db,
        isbn=isbn,
        title=title,
        author=author,
        genre=genre,
        year=year,
        unit_price=unit_price,
        cover_url=cover_url,
    )
    return {"id": book.id, "title": book.title}


# -----------------------------
# READ
# -----------------------------
@router.get("/{book_id}", response_model=dict)
def read_book(book_id: int, db: Session = Depends(get_db)):
    book = crud_book.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {
        "id": book.id,
        "isbn": book.isbn,
        "title": book.title,
        "author": book.author,
        "genre": book.genre,
        "year": book.year,
        "unit_price": str(book.unit_price),
        "cover_url": book.cover_url,
        "created_at": str(book.created_at),
    }


@router.get("", response_model=list[dict])
def list_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    books = crud_book.get_books(db, skip=skip, limit=limit)
    return [
        {
            "id": b.id,
            "isbn": b.isbn,
            "title": b.title,
            "author": b.author,
            "genre": b.genre,
            "year": b.year,
            "unit_price": str(b.unit_price),
            "cover_url": b.cover_url,
            "created_at": str(b.created_at),
        }
        for b in books
    ]


# -----------------------------
# UPDATE
# -----------------------------
@router.put("/{book_id}", response_model=dict)
def update_book(
    book_id: int,
    title: str | None | None,
    author: str | None | None,
    genre: str | None | None,
    year: int | None | None,
    unit_price: float | None | None,
    cover_url: str | None | None,
    db: Session = Depends(get_db),
):
    book = crud_book.update_book(
        db=db,
        book_id=book_id,
        title=title,
        author=author,
        genre=genre,
        year=year,
        unit_price=unit_price,
        cover_url=cover_url,
    )
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"id": book.id, "title": book.title}


# -----------------------------
# DELETE
# -----------------------------
@router.delete("/{book_id}", response_model=dict)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    success = crud_book.delete_book(db, book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"deleted": True}
