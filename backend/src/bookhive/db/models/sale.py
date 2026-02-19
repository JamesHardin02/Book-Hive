from datetime import date
from bookhive.db.base import Base
from sqlalchemy import Integer, ForeignKey, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal


class Sale(Base):
    __tablename__ = "sale"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), index=True, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    member_id: Mapped[int] = mapped_column(ForeignKey("member.id"), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    sold_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
    
    book = relationship("Book", back_populates="sales")
    member = relationship("Member", back_populates="sales")
