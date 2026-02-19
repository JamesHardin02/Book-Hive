from bookhive.db.base import Base
from sqlalchemy import String, Integer, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from decimal import Decimal


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    author: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    genre: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    cover_url: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    inventory = relationship("Inventory", back_populates="book")
    stock_adjustments = relationship("Stock_Adjustment", back_populates="book")
    sales = relationship("Sale", back_populates="book")
    loans = relationship("Loan", back_populates="book")
