from bookhive.db.base import Base
from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Location(Base):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    aisle: Mapped[int] = mapped_column(Integer, nullable=False)
    shelf: Mapped[int] = mapped_column(Integer, nullable=False)
    
    inventory = relationship("Inventory", back_populates="location")

    __table_args__ = (UniqueConstraint("aisle", "shelf"))
