from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from bookhive.schemas.inventory import InventoryOut
from bookhive.schemas.locations import LocationCreate


def _digits_only(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())


class BookCreate(BaseModel):
    isbn: str = Field(min_length=10, max_length=32)
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    genre: str = Field(min_length=1, max_length=255)
    year: int = Field(ge=0, le=3000)
    unit_price: Decimal | None = None
    cover_url: str | None = None

    # Inventory/Location included on create
    initial_on_hand: int = Field(default=0, ge=0)
    location: LocationCreate | None = None

    # FR13 behavior:
    # - by default, duplicate ISBN is blocked (same edition)
    # - allow_new_edition will auto-increment edition if isbn exists
    allow_new_edition: bool = False
    edition: int | None = Field(default=None, ge=1)

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v: str) -> str:
        # Accept hyphenated ISBN; normalize to digits for storage
        digits = _digits_only(v)
        if len(digits) not in (10, 13):
            raise ValueError("ISBN must be 10 or 13 digits (hyphens allowed)")
        return digits


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    genre: str | None = Field(default=None, min_length=1, max_length=255)
    year: int | None = Field(default=None, ge=0, le=3000)
    unit_price: Decimal | None = None
    cover_url: str | None = None


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    isbn: str
    edition: int
    title: str
    author: str
    genre: str
    year: int
    unit_price: Decimal | None
    cover_url: str | None
    created_at: date

    inventory: InventoryOut | None


class BookLookupOut(BaseModel):
    isbn: str
    title: str | None
    authors: list[str]
    publish_year: int | None
    cover_url: str | None
