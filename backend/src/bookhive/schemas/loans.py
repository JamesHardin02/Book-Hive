from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class LoanCreate(BaseModel):
    book_id: int = Field(gt=0)
    member_id: int = Field(gt=0)
    due_date: date


class LoanBookSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    isbn: str
    edition: int


class LoanMemberSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: date
    due_date: date
    returned_at: date | None

    book: LoanBookSummary
    member: LoanMemberSummary
