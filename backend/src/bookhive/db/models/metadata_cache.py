from datetime import date

from bookhive.db.base import Base
from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column


class Metadata_Cache(Base):
    __tablename__ = "metadata_cache"

    isbn: Mapped[str] = mapped_column(primary_key=True)
    payload: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    fetched_at: Mapped[date] = mapped_column(Date, default=date.today, nullable=False)
