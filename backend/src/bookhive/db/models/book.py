from datetime import date
from decimal import Decimal

from bookhive.db.base import Base
from sqlalchemy import Date, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(String(13), nullable=False)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    author: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    genre: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    edition: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    # relationships used with mapped function rather than assigning to variable?
    inventory = relationship("Inventory", back_populates="book", uselist=False)
    stock_adjustments = relationship("Stock_Adjustment", back_populates="book")
    sales = relationship("Sale", back_populates="book")
    loans = relationship("Loan", back_populates="book")

    __table_args__ = (UniqueConstraint("isbn", "edition", name="uq_book_isbn_edition"),)
