from datetime import date

from bookhive.db.base import Base
from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Member(Base):
    __tablename__ = "member"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    sales = relationship("Sale", back_populates="member")
    loans = relationship("Loan", back_populates="member")
