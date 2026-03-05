import argparse
import os
import sys
import logging
from datetime import date, timedelta
from decimal import Decimal

logging.getLogger("passlib").setLevel(logging.ERROR)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Allow running from backend/ without installing as package
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from sqlalchemy.orm import Session  # noqa: E402

from bookhive.auth.security import hash_password  # noqa: E402
from bookhive.db.base import Base  # noqa: E402
from bookhive.db.engine import SessionLocal, engine  # noqa: E402
from bookhive.db.models.book import Book  # noqa: E402
from bookhive.db.models.inventory import Inventory  # noqa: E402
from bookhive.db.models.loan import Loan  # noqa: E402
from bookhive.db.models.location import Location  # noqa: E402
from bookhive.db.models.member import Member  # noqa: E402
from bookhive.db.models.sale import Sale  # noqa: E402
from bookhive.db.models.stock_adjustment import Stock_Adjustment  # noqa: E402
from bookhive.db.models.user import User  # noqa: E402
from bookhive.db.models.app_setting import AppSetting  # noqa: E402


def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_or_create(db: Session, model, defaults=None, **kwargs):
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    params = dict(kwargs)
    if defaults:
        params.update(defaults)
    instance = model(**params)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance, True


def seed(db: Session) -> None:
    # Admin/manager account
    manager, _ = get_or_create(
        db,
        User,
        username="manager",
        defaults={
            "email": "manager@example.com",
            "hashed_password": hash_password("manager123"),
            "is_admin": True,
            "is_active": True,
        },
    )

    get_or_create(
        db,
        AppSetting,
        key="low_stock_threshold",
        defaults={"int_value": 3},
    )

    # Locations
    loc_a1, _ = get_or_create(db, Location, aisle="B", shelf="2")
    loc_b2, _ = get_or_create(db, Location, aisle="E", shelf="1")

    # Books
    book1, _ = get_or_create(
        db,
        Book,
        isbn="9780140328721",
        edition=1,
        defaults={
            "title": "Matilda",
            "author": "Roald Dahl",
            "genre": "Fiction",
            "year": 1988,
            "unit_price": None,
            "cover_url": None,
        },
    )

    book2, _ = get_or_create(
        db,
        Book,
        isbn="9780061120084",
        edition=1,
        defaults={
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "genre": "Fiction",
            "year": 1960,
            "unit_price": None,
            "cover_url": None,
        },
    )

    # Inventory
    get_or_create(
        db,
        Inventory,
        book_id=book1.id,
        defaults={"on_hand": 5, "location_id": loc_a1.id},
    )
    get_or_create(
        db,
        Inventory,
        book_id=book2.id,
        defaults={"on_hand": 2, "location_id": loc_b2.id},
    )

    # Member
    member, _ = get_or_create(
        db,
        Member,
        email="member@example.com",
        defaults={
            "name": "John Doe",
            "phone_number": "555-0000",
            "created_at": date.today(),
        },
    )

    # Example loan (active)
    get_or_create(
        db,
        Loan,
        book_id=book1.id,
        member_id=member.id,
        defaults={
            "created_at": date.today(),
            "due_date": date.today() + timedelta(days=14),
            "returned_at": None,
        },
    )

    # Example sale
    get_or_create(
        db,
        Sale,
        book_id=book2.id,
        member_id=member.id,
        defaults={
            "quantity": 1,
            "unit_price": Decimal("9.99"),
            "sold_at": date.today(),
        },
    )

    # Example stock adjustment (audit entity)
    get_or_create(
        db,
        Stock_Adjustment,
        book_id=book1.id,
        user_id=manager.id,
        defaults={"delta": 2, "reason": "Initial stock", "created_at": date.today()},
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset", action="store_true", help="Drop and recreate tables before seeding"
    )
    args = parser.parse_args()

    if args.reset:
        reset_db()

    db = SessionLocal()
    try:
        seed(db)
        print("Seed completed.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
