from bookhive.db.base import Base
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column


class Metadata_Cache(Base):
    __tablename__ = "metadata_cache"

    isbn: Mapped[int] = mapped_column(primary_key=True)
    payload: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    # Is fetched_at a date or string?
    fetched_at: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    