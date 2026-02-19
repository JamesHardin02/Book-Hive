from bookhive.db.base import Base
from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Inventory(Base):
    __tablename__ = "inventory"

    book_id: Mapped[int] = mapped_column(
        ForeignKey("book.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("location.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    on_hand: Mapped[int] = mapped_column(Integer, nullable=False)
    min_threshold: Mapped[int] = mapped_column(Integer, nullable=False)

    book = relationship("Book", back_populates="inventory", passive_deletes=True)
    location = relationship("Location", back_populates="inventory", passive_deletes=True)

    __table_args__ = (
        CheckConstraint("on_hand >= 0", name="ck_inventory_on_hand_nonnegative"),
        CheckConstraint("min_threshold >= 0"),
    )
