from datetime import datetime, timezone

from bookhive.db.base import Base
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class Metadata_Cache(Base):
    __tablename__ = "metadata_cache"

    isbn: Mapped[str] = mapped_column(String(32), primary_key=True)

    # JSON string; Text avoids truncation.
    payload: Mapped[str] = mapped_column(Text, nullable=False)

    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )