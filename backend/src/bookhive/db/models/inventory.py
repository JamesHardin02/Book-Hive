from bookhive.db.base import Base
from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Inventory(Base):
    __tablename__ = "inventory"

    # One row per book. Deleting a book deletes inventory.
    book_id: Mapped[int] = mapped_column(
        ForeignKey("book.id", ondelete="CASCADE"), primary_key=True, index=True
    )

    # Location can be assigned later; if a location is deleted, just unset it.
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("location.id", ondelete="SET NULL"), nullable=True, index=True
    )

    on_hand: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    min_threshold: Mapped[int | None] = mapped_column(Integer, nullable=True)

    book = relationship("Book", back_populates="inventory", passive_deletes=True)
    location = relationship("Location", back_populates="inventory")

    __table_args__ = (
        CheckConstraint("on_hand >= 0", name="ck_inventory_on_hand_nonnegative"),
        CheckConstraint(
            "min_threshold IS NULL OR min_threshold >= 0", name="ck_min_threshold_nonnegative"
        ),
    )
