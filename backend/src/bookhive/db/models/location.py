from bookhive.db.base import Base
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Location(Base):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    aisle: Mapped[str] = mapped_column(String(20), nullable=False)
    shelf: Mapped[str] = mapped_column(String(20), nullable=False)

    inventory = relationship("Inventory", back_populates="location")

    __table_args__ = (UniqueConstraint("aisle", "shelf", name="uq_location_aisle_shelf"),)
