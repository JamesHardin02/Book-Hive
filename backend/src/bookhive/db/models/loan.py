from datetime import date

from bookhive.db.base import Base
from sqlalchemy import CheckConstraint, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Loan(Base):
    __tablename__ = "loan"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), index=True, nullable=False)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"), index=True, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    returned_at: Mapped[date] = mapped_column(Date, nullable=True, default=None)

    book = relationship("Book", back_populates="loans")
    member = relationship("Member", back_populates="loans")

    __table_args__ = (CheckConstraint("due_date >= created_at", name="check_due_date"),)
