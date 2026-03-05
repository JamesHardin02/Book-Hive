from fastapi import APIRouter, Depends, HTTPException, Query

from bookhive.auth.dependencies import get_current_user
from bookhive.db.models.user import User
from bookhive.schemas.books import BookCreate, BookLookupOut, BookOut, BookUpdate
from bookhive.schemas.inventory import InventoryOut, StockAdjustIn, ThresholdUpdateIn
from bookhive.services.book_service import BookService
from bookhive.services.deps import (
    get_book_service,
    get_inventory_service,
    get_openlibrary_service,
)
from bookhive.services.inventory_service import InventoryService
from bookhive.services.openlibrary_service import OpenLibraryService

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/lookup", response_model=BookLookupOut)
def lookup(
    isbn: str = Query(..., min_length=10, max_length=32),
    svc: OpenLibraryService = Depends(get_openlibrary_service),
    _: User = Depends(get_current_user),
):
    isbn = "".join(ch for ch in isbn if ch.isdigit())
    data = svc.lookup_isbn(isbn=isbn)
    if not data:
        raise HTTPException(status_code=404, detail="ISBN not found")
    return data


@router.post("", response_model=BookOut, status_code=201)
def create_book(
    payload: BookCreate,
    svc: BookService = Depends(get_book_service),
    _: User = Depends(get_current_user),
):
    book = svc.create_book(
        isbn=payload.isbn,
        title=payload.title,
        author=payload.author,
        genre=payload.genre,
        year=payload.year,
        unit_price=payload.unit_price,
        cover_url=payload.cover_url,
        initial_on_hand=payload.initial_on_hand,
        location=None if payload.location is None else payload.location.model_dump(),
        allow_new_edition=payload.allow_new_edition,
        edition=payload.edition,
    )
    return book


@router.get("/{book_id}", response_model=BookOut)
def get_book(
    book_id: int, svc: BookService = Depends(get_book_service), _: User = Depends(get_current_user)
):
    return svc.get_book(book_id=book_id)


@router.get("", response_model=list[BookOut])
def list_books(
    q: str | None = None,
    title: str | None = None,
    author: str | None = None,
    isbn: str | None = None,
    genre: str | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    svc: BookService = Depends(get_book_service),
    _: User = Depends(get_current_user),
):
    return svc.search(
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


@router.patch("/{book_id}", response_model=BookOut)
def update_book(
    book_id: int,
    payload: BookUpdate,
    svc: BookService = Depends(get_book_service),
    _: User = Depends(get_current_user),
):
    return svc.update_book(book_id=book_id, **payload.model_dump(exclude_unset=True))


@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: int, svc: BookService = Depends(get_book_service), _: User = Depends(get_current_user)
):
    svc.delete_book(book_id=book_id)
    return None


@router.patch("/{book_id}/stock", response_model=InventoryOut)
def adjust_stock(
    book_id: int,
    payload: StockAdjustIn,
    inv: InventoryService = Depends(get_inventory_service),
    user: User = Depends(get_current_user),
):
    return inv.adjust_stock(
        book_id=book_id, user_id=user.id, delta=payload.delta, reason=payload.reason
    )


@router.patch("/{book_id}/location", response_model=InventoryOut)
def set_location(
    book_id: int,
    aisle: str,
    shelf: str,
    inv: InventoryService = Depends(get_inventory_service),
    _: User = Depends(get_current_user),
):
    return inv.set_location(book_id=book_id, aisle=aisle, shelf=shelf)


@router.patch("/{book_id}/min-threshold", response_model=InventoryOut)
def set_min_threshold(
    book_id: int,
    payload: ThresholdUpdateIn,
    inv: InventoryService = Depends(get_inventory_service),
    _: User = Depends(get_current_user),
):
    return inv.set_min_threshold(book_id=book_id, min_threshold=payload.min_threshold)
