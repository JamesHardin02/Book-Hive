from datetime import date
from bookhive.db.base import Base
from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Stock_Adjustment(Base):
    __tablename__ = "stock_adjustment"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id"), nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)

    book = relationship("Book", back_populates="stock_adjustments")
    user = relationship("User", back_populates="stock_adjustments")
