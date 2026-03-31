import argparse
import logging
import os
import sys
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
from bookhive.db.models.app_setting import AppSetting  # noqa: E402
from bookhive.db.models.book import Book  # noqa: E402
from bookhive.db.models.inventory import Inventory  # noqa: E402
from bookhive.db.models.loan import Loan  # noqa: E402
from bookhive.db.models.location import Location  # noqa: E402
from bookhive.db.models.member import Member  # noqa: E402
from bookhive.db.models.sale import Sale  # noqa: E402
from bookhive.db.models.stock_adjustment import Stock_Adjustment  # noqa: E402
from bookhive.db.models.user import User  # noqa: E402


def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def upsert(db: Session, model, lookup: dict, values: dict | None = None):
    """
    Simple upsert helper:
    - finds by lookup fields
    - updates value fields if found
    - creates the row otherwise
    """
    row = db.query(model).filter_by(**lookup).first()
    if row:
        changed = False
        for key, value in (values or {}).items():
            if getattr(row, key) != value:
                setattr(row, key, value)
                changed = True
        if changed:
            db.commit()
            db.refresh(row)
        return row, False

    payload = dict(lookup)
    if values:
        payload.update(values)

    row = model(**payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row, True


def money(value: str | None) -> Decimal | None:
    return None if value is None else Decimal(value)


def seed_locations(db: Session) -> dict[str, Location]:
    location_specs = [
        ("A", "1"),
        ("A", "2"),
        ("A", "3"),
        ("B", "1"),
        ("B", "2"),
        ("B", "3"),
        ("C", "1"),
        ("C", "2"),
        ("C", "3"),
        ("D", "1"),
        ("D", "2"),
        ("D", "3"),
        ("E", "1"),
        ("E", "2"),
        ("F", "1"),
        ("F", "2"),
    ]

    locations: dict[str, Location] = {}
    for aisle, shelf in location_specs:
        loc, _ = upsert(
            db,
            Location,
            lookup={"aisle": aisle, "shelf": shelf},
        )
        locations[f"{aisle}-{shelf}"] = loc

    return locations


def seed_books_and_inventory(
    db: Session, locations: dict[str, Location]
) -> dict[str, Book]:
    """
    Returns a dict keyed by '<isbn>|<edition>' for easy lookups later.
    """
    catalog = [
        {
            "isbn": "9780140328721",
            "edition": 1,
            "title": "Matilda",
            "author": "Roald Dahl",
            "genre": "Children's",
            "year": 1988,
            "unit_price": "8.99",
            "cover_url": None,
            "location": "B-2",
            "on_hand": 4,
            "min_threshold": 3,
        },
        {
            "isbn": "9780061120084",
            "edition": 1,
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "genre": "Fiction",
            "year": 1960,
            "unit_price": "10.99",
            "cover_url": None,
            "location": "E-1",
            "on_hand": 2,
            "min_threshold": 2,
        },
        {
            "isbn": "9780451524935",
            "edition": 1,
            "title": "1984",
            "author": "George Orwell",
            "genre": "Fiction",
            "year": 1949,
            "unit_price": "9.99",
            "cover_url": None,
            "location": "C-1",
            "on_hand": 7,
            "min_threshold": 3,
        },
        {
            "isbn": "9780441172719",
            "edition": 1,
            "title": "Dune",
            "author": "Frank Herbert",
            "genre": "Science & Mathematics",
            "year": 1965,
            "unit_price": "14.99",
            "cover_url": None,
            "location": "D-1",
            "on_hand": 1,
            "min_threshold": 2,
        },
        {
            "isbn": "9780345339683",
            "edition": 1,
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "genre": "Fiction",
            "year": 1937,
            "unit_price": "11.99",
            "cover_url": None,
            "location": "C-2",
            "on_hand": 5,
            "min_threshold": 3,
        },
        {
            "isbn": "9780064402054",
            "edition": 1,
            "title": "Charlotte's Web",
            "author": "E.B. White",
            "genre": "Children's",
            "year": 1952,
            "unit_price": "7.99",
            "cover_url": None,
            "location": "B-1",
            "on_hand": 3,
            "min_threshold": 3,
        },
        {
            "isbn": "9780743273565",
            "edition": 1,
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "genre": "Fiction",
            "year": 1925,
            "unit_price": "10.49",
            "cover_url": None,
            "location": "A-1",
            "on_hand": 8,
            "min_threshold": 3,
        },
        {
            "isbn": "9780394800011",
            "edition": 1,
            "title": "The Cat in the Hat",
            "author": "Dr. Seuss",
            "genre": "Children's",
            "year": 1957,
            "unit_price": "6.99",
            "cover_url": None,
            "location": "B-3",
            "on_hand": 0,
            "min_threshold": 2,
        },
        {
            "isbn": "9780062316094",
            "edition": 1,
            "title": "Sapiens",
            "author": "Yuval Noah Harari",
            "genre": "History",
            "year": 2011,
            "unit_price": "18.99",
            "cover_url": None,
            "location": "E-2",
            "on_hand": 2,
            "min_threshold": 4,
        },
        {
            "isbn": "9780399590504",
            "edition": 1,
            "title": "Educated",
            "author": "Tara Westover",
            "genre": "Biography",
            "year": 2018,
            "unit_price": "16.99",
            "cover_url": None,
            "location": "E-1",
            "on_hand": 6,
            "min_threshold": 3,
        },
        {
            "isbn": "9780062315004",
            "edition": 1,
            "title": "The Alchemist",
            "author": "Paulo Coelho",
            "genre": "Fiction",
            "year": 1988,
            "unit_price": "12.99",
            "cover_url": None,
            "location": "A-2",
            "on_hand": 9,
            "min_threshold": 3,
        },
        {
            "isbn": "9780735211292",
            "edition": 1,
            "title": "Atomic Habits",
            "author": "James Clear",
            "genre": "Health & Wellness",
            "year": 2018,
            "unit_price": "17.99",
            "cover_url": None,
            "location": "F-1",
            "on_hand": 1,
            "min_threshold": 2,
        },
        {
            "isbn": "9780553380163",
            "edition": 1,
            "title": "A Brief History of Time",
            "author": "Stephen Hawking",
            "genre": "Science & Mathematics",
            "year": 1988,
            "unit_price": "15.99",
            "cover_url": None,
            "location": "D-2",
            "on_hand": 4,
            "min_threshold": 2,
        },
        {
            "isbn": "9780201616224",
            "edition": 1,
            "title": "The Pragmatic Programmer",
            "author": "Andrew Hunt",
            "genre": "Textbooks",
            "year": 1999,
            "unit_price": "29.99",
            "cover_url": None,
            "location": "F-2",
            "on_hand": 5,
            "min_threshold": 2,
        },
        {
            "isbn": "9780132350884",
            "edition": 1,
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "genre": "Textbooks",
            "year": 2008,
            "unit_price": "31.99",
            "cover_url": None,
            "location": "F-2",
            "on_hand": 2,
            "min_threshold": 2,
        },
        {
            "isbn": "9780141439518",
            "edition": 1,
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "genre": "Fiction",
            "year": 1813,
            "unit_price": "8.49",
            "cover_url": None,
            "location": "A-3",
            "on_hand": 7,
            "min_threshold": 3,
        },
        {
            "isbn": "9780375842207",
            "edition": 1,
            "title": "The Book Thief",
            "author": "Markus Zusak",
            "genre": "Fiction",
            "year": 2005,
            "unit_price": "12.49",
            "cover_url": None,
            "location": "C-3",
            "on_hand": 4,
            "min_threshold": 2,
        },
        {
            "isbn": "9780590353427",
            "edition": 1,
            "title": "Harry Potter and the Sorcerer's Stone",
            "author": "J.K. Rowling",
            "genre": "Children's",
            "year": 1997,
            "unit_price": "10.99",
            "cover_url": None,
            "location": "B-2",
            "on_hand": 6,
            "min_threshold": 3,
        },
        {
            "isbn": "9780590353427",
            "edition": 2,
            "title": "Harry Potter and the Sorcerer's Stone",
            "author": "J.K. Rowling",
            "genre": "Children's",
            "year": 1999,
            "unit_price": "14.99",
            "cover_url": None,
            "location": "B-2",
            "on_hand": 1,
            "min_threshold": 2,
        },
        {
            "isbn": "9781501124020",
            "edition": 1,
            "title": "It Ends with Us",
            "author": "Colleen Hoover",
            "genre": "Fiction",
            "year": 2016,
            "unit_price": "13.99",
            "cover_url": None,
            "location": "A-1",
            "on_hand": 0,
            "min_threshold": 2,
        },
    ]

    book_index: dict[str, Book] = {}

    for item in catalog:
        book, _ = upsert(
            db,
            Book,
            lookup={"isbn": item["isbn"], "edition": item["edition"]},
            values={
                "title": item["title"],
                "author": item["author"],
                "genre": item["genre"],
                "year": item["year"],
                "unit_price": money(item["unit_price"]),
                "cover_url": item["cover_url"],
            },
        )

        loc = locations[item["location"]]
        upsert(
            db,
            Inventory,
            lookup={"book_id": book.id},
            values={
                "on_hand": item["on_hand"],
                "location_id": loc.id,
                "min_threshold": item["min_threshold"],
            },
        )

        book_index[f"{item['isbn']}|{item['edition']}"] = book

    return book_index


def seed_members(db: Session) -> dict[str, Member]:
    today = date.today()

    member_specs = [
        ("john.doe@example.com", "John Doe", "555-0001", today - timedelta(days=220)),
        (
            "maya.patel@example.com",
            "Maya Patel",
            "555-0002",
            today - timedelta(days=205),
        ),
        (
            "liam.carter@example.com",
            "Liam Carter",
            "555-0003",
            today - timedelta(days=180),
        ),
        (
            "olivia.reed@example.com",
            "Olivia Reed",
            "555-0004",
            today - timedelta(days=165),
        ),
        (
            "ethan.price@example.com",
            "Ethan Price",
            "555-0005",
            today - timedelta(days=140),
        ),
        (
            "ava.morris@example.com",
            "Ava Morris",
            "555-0006",
            today - timedelta(days=120),
        ),
        (
            "noah.turner@example.com",
            "Noah Turner",
            "555-0007",
            today - timedelta(days=90),
        ),
        (
            "sofia.gray@example.com",
            "Sofia Gray",
            "555-0008",
            today - timedelta(days=75),
        ),
        (
            "elijah.wilson@example.com",
            "Elijah Wilson",
            "555-0009",
            today - timedelta(days=50),
        ),
        (
            "isabella.king@example.com",
            "Isabella King",
            "555-0010",
            today - timedelta(days=30),
        ),
    ]

    member_index: dict[str, Member] = {}
    for email, name, phone_number, created_at in member_specs:
        member, _ = upsert(
            db,
            Member,
            lookup={"email": email},
            values={
                "name": name,
                "phone_number": phone_number,
                "created_at": created_at,
            },
        )
        member_index[email] = member

    return member_index


def seed_loans(db: Session, books: dict[str, Book], members: dict[str, Member]) -> None:
    """
    Seed a mix of:
    - overdue
    - due soon
    - active not due soon
    - returned
    """
    today = date.today()

    loan_specs = [
        # overdue
        {
            "book_key": "9780140328721|1",
            "member_email": "john.doe@example.com",
            "created_at": today - timedelta(days=21),
            "due_date": today - timedelta(days=5),
            "returned_at": None,
        },
        {
            "book_key": "9780441172719|1",
            "member_email": "maya.patel@example.com",
            "created_at": today - timedelta(days=16),
            "due_date": today - timedelta(days=2),
            "returned_at": None,
        },
        {
            "book_key": "9780062316094|1",
            "member_email": "liam.carter@example.com",
            "created_at": today - timedelta(days=30),
            "due_date": today - timedelta(days=10),
            "returned_at": None,
        },
        {
            "book_key": "9780590353427|2",
            "member_email": "olivia.reed@example.com",
            "created_at": today - timedelta(days=12),
            "due_date": today - timedelta(days=1),
            "returned_at": None,
        },
        # due soon
        {
            "book_key": "9780451524935|1",
            "member_email": "ethan.price@example.com",
            "created_at": today - timedelta(days=9),
            "due_date": today + timedelta(days=1),
            "returned_at": None,
        },
        {
            "book_key": "9780345339683|1",
            "member_email": "ava.morris@example.com",
            "created_at": today - timedelta(days=10),
            "due_date": today + timedelta(days=3),
            "returned_at": None,
        },
        {
            "book_key": "9780132350884|1",
            "member_email": "noah.turner@example.com",
            "created_at": today - timedelta(days=7),
            "due_date": today + timedelta(days=5),
            "returned_at": None,
        },
        {
            "book_key": "9780735211292|1",
            "member_email": "sofia.gray@example.com",
            "created_at": today - timedelta(days=4),
            "due_date": today + timedelta(days=7),
            "returned_at": None,
        },
        # active, not due soon
        {
            "book_key": "9780743273565|1",
            "member_email": "elijah.wilson@example.com",
            "created_at": today - timedelta(days=2),
            "due_date": today + timedelta(days=14),
            "returned_at": None,
        },
        {
            "book_key": "9780201616224|1",
            "member_email": "isabella.king@example.com",
            "created_at": today - timedelta(days=1),
            "due_date": today + timedelta(days=21),
            "returned_at": None,
        },
        {
            "book_key": "9780375842207|1",
            "member_email": "john.doe@example.com",
            "created_at": today,
            "due_date": today + timedelta(days=30),
            "returned_at": None,
        },
        # returned
        {
            "book_key": "9780061120084|1",
            "member_email": "maya.patel@example.com",
            "created_at": today - timedelta(days=28),
            "due_date": today - timedelta(days=14),
            "returned_at": today - timedelta(days=13),
        },
        {
            "book_key": "9780064402054|1",
            "member_email": "liam.carter@example.com",
            "created_at": today - timedelta(days=18),
            "due_date": today - timedelta(days=6),
            "returned_at": today - timedelta(days=4),
        },
        {
            "book_key": "9780399590504|1",
            "member_email": "olivia.reed@example.com",
            "created_at": today - timedelta(days=20),
            "due_date": today - timedelta(days=3),
            "returned_at": today - timedelta(days=1),
        },
        {
            "book_key": "9780141439518|1",
            "member_email": "ava.morris@example.com",
            "created_at": today - timedelta(days=15),
            "due_date": today + timedelta(days=1),
            "returned_at": today - timedelta(days=2),
        },
    ]

    for item in loan_specs:
        book = books[item["book_key"]]
        member = members[item["member_email"]]

        upsert(
            db,
            Loan,
            lookup={
                "book_id": book.id,
                "member_id": member.id,
                "created_at": item["created_at"],
                "due_date": item["due_date"],
                "returned_at": item["returned_at"],
            },
        )


def seed_sales(db: Session, books: dict[str, Book], members: dict[str, Member]) -> None:
    today = date.today()

    sales_specs = [
        (
            "9780061120084|1",
            "john.doe@example.com",
            1,
            "10.99",
            today - timedelta(days=180),
        ),
        ("9780743273565|1", None, 2, "10.49", today - timedelta(days=165)),
        (
            "9780735211292|1",
            "maya.patel@example.com",
            1,
            "17.99",
            today - timedelta(days=150),
        ),
        ("9780201616224|1", None, 1, "29.99", today - timedelta(days=145)),
        (
            "9780132350884|1",
            "liam.carter@example.com",
            1,
            "31.99",
            today - timedelta(days=130),
        ),
        ("9780375842207|1", None, 3, "12.49", today - timedelta(days=118)),
        (
            "9780062315004|1",
            "olivia.reed@example.com",
            2,
            "12.99",
            today - timedelta(days=95),
        ),
        ("9780399590504|1", None, 1, "16.99", today - timedelta(days=82)),
        (
            "9780451524935|1",
            "ethan.price@example.com",
            1,
            "9.99",
            today - timedelta(days=70),
        ),
        ("9780553380163|1", None, 1, "15.99", today - timedelta(days=58)),
        (
            "9780590353427|1",
            "ava.morris@example.com",
            2,
            "10.99",
            today - timedelta(days=45),
        ),
        ("9780140328721|1", None, 1, "8.99", today - timedelta(days=30)),
        (
            "9781501124020|1",
            "noah.turner@example.com",
            1,
            "13.99",
            today - timedelta(days=14),
        ),
        ("9780441172719|1", None, 1, "14.99", today - timedelta(days=7)),
        (
            "9780062316094|1",
            "sofia.gray@example.com",
            1,
            "18.99",
            today - timedelta(days=2),
        ),
    ]

    for book_key, member_email, quantity, unit_price, sold_at in sales_specs:
        book = books[book_key]
        member_id = None if member_email is None else members[member_email].id

        upsert(
            db,
            Sale,
            lookup={
                "book_id": book.id,
                "member_id": member_id,
                "quantity": quantity,
                "unit_price": Decimal(unit_price),
                "sold_at": sold_at,
            },
        )


def seed_stock_adjustments(
    db: Session,
    books: dict[str, Book],
    manager: User,
) -> None:
    today = date.today()

    adjustment_specs = [
        ("9780140328721|1", 8, "Initial catalog load", today - timedelta(days=220)),
        ("9780061120084|1", 6, "Initial catalog load", today - timedelta(days=220)),
        ("9780451524935|1", 10, "Initial catalog load", today - timedelta(days=220)),
        ("9780441172719|1", 4, "Initial catalog load", today - timedelta(days=220)),
        ("9780345339683|1", 8, "Initial catalog load", today - timedelta(days=220)),
        ("9780394800011|1", 5, "Initial catalog load", today - timedelta(days=220)),
        ("9780062316094|1", 5, "Initial catalog load", today - timedelta(days=220)),
        ("9780735211292|1", 4, "Initial catalog load", today - timedelta(days=220)),
        ("9780201616224|1", 4, "Initial catalog load", today - timedelta(days=220)),
        ("9780132350884|1", 4, "Initial catalog load", today - timedelta(days=220)),
        ("9780590353427|1", 10, "Initial catalog load", today - timedelta(days=220)),
        (
            "9780590353427|2",
            2,
            "Added second edition for demo",
            today - timedelta(days=120),
        ),
        ("9780441172719|1", 3, "Received restock", today - timedelta(days=60)),
        ("9780441172719|1", -2, "Damaged copies removed", today - timedelta(days=20)),
        ("9780735211292|1", 2, "Small restock", today - timedelta(days=35)),
        ("9780735211292|1", -1, "Shelf count correction", today - timedelta(days=5)),
        ("9781501124020|1", 4, "New title received", today - timedelta(days=25)),
        ("9781501124020|1", -2, "Weekend sale correction", today - timedelta(days=12)),
        (
            "9780394800011|1",
            -3,
            "Promotional clearance and damaged copy removal",
            today - timedelta(days=15),
        ),
        ("9780062316094|1", -1, "Lost copy write-off", today - timedelta(days=8)),
    ]

    for book_key, delta, reason, created_at in adjustment_specs:
        book = books[book_key]

        upsert(
            db,
            Stock_Adjustment,
            lookup={
                "book_id": book.id,
                "user_id": manager.id,
                "delta": delta,
                "reason": reason,
                "created_at": created_at,
            },
        )


def seed(db: Session) -> None:
    manager, _ = upsert(
        db,
        User,
        lookup={"username": "manager"},
        values={
            "email": "manager@example.com",
            "hashed_password": hash_password("manager123"),
            "is_admin": True,
            "is_active": True,
        },
    )

    upsert(
        db,
        AppSetting,
        lookup={"key": "low_stock_threshold"},
        values={"int_value": 3},
    )

    locations = seed_locations(db)
    books = seed_books_and_inventory(db, locations)
    members = seed_members(db)
    seed_loans(db, books, members)
    seed_sales(db, books, members)
    seed_stock_adjustments(db, books, manager)

    today = date.today()
    overdue_count = (
        db.query(Loan)
        .filter(Loan.returned_at.is_(None))
        .filter(Loan.due_date < today)
        .count()
    )
    due_soon_count = (
        db.query(Loan)
        .filter(Loan.returned_at.is_(None))
        .filter(Loan.due_date >= today)
        .filter(Loan.due_date <= today + timedelta(days=7))
        .count()
    )
    active_count = (
        db.query(Loan)
        .filter(Loan.returned_at.is_(None))
        .filter(Loan.due_date > today + timedelta(days=7))
        .count()
    )
    returned_count = db.query(Loan).filter(Loan.returned_at.is_not(None)).count()

    print("Seed completed.")
    print("Manager login: manager@example.com / manager123")
    print(f"Books: {db.query(Book).count()}")
    print(f"Members: {db.query(Member).count()}")
    print(f"Locations: {db.query(Location).count()}")
    print(f"Loans: {db.query(Loan).count()}")
    print(f"  - overdue: {overdue_count}")
    print(f"  - due soon: {due_soon_count}")
    print(f"  - active later: {active_count}")
    print(f"  - returned: {returned_count}")
    print(f"Sales: {db.query(Sale).count()}")
    print(f"Stock adjustments: {db.query(Stock_Adjustment).count()}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate tables before seeding",
    )
    args = parser.parse_args()

    if args.reset:
        reset_db()

    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
