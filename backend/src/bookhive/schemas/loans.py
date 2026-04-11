from datetime import date, timedelta

from pydantic import BaseModel, ConfigDict, Field, computed_field

DUE_SOON_DAYS = 7


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

    @computed_field
    @property
    def status(self) -> str:
        today = date.today()

        if self.returned_at is not None:
            return "returned"
        if self.due_date < today:
            return "overdue"
        if self.due_date <= today + timedelta(days=DUE_SOON_DAYS):
            return "due_soon"
        return "active"

    @computed_field
    @property
    def due_soon(self) -> bool:
        return self.status == "due_soon"

    @computed_field
    @property
    def days_until_due(self) -> int | None:
        if self.returned_at is not None:
            return None
        return (self.due_date - date.today()).days
