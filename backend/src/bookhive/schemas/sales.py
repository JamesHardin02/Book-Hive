from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SaleCreate(BaseModel):
    book_id: int = Field(gt=0)
    member_id: int | None = None
    quantity: int = Field(ge=1, le=100000)
    unit_price: Decimal = Field(ge=0)


class SaleBookSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    isbn: str
    edition: int


class SaleMemberSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class SaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity: int
    unit_price: Decimal
    sold_at: date

    book: SaleBookSummary
    member: SaleMemberSummary | None
