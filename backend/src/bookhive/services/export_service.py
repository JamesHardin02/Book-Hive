from __future__ import annotations

import csv
from datetime import date, timedelta
from decimal import Decimal
from io import StringIO

from bookhive.db.models.book import Book
from bookhive.db.models.inventory import Inventory
from bookhive.db.models.loan import Loan
from bookhive.db.models.member import Member
from bookhive.db.models.sale import Sale
from sqlalchemy.orm import Session, joinedload


def _new_csv_buffer() -> tuple[StringIO, csv.writer]:
    """
    Start CSV with UTF-8 BOM so Excel on Windows opens it cleanly.
    """
    buffer = StringIO()
    buffer.write("\ufeff")
    return buffer, csv.writer(buffer)


def _money(value: Decimal | None) -> str:
    return "" if value is None else str(value)


def _loan_status(loan: Loan, due_soon_days: int = 7) -> str:
    today = date.today()

    if loan.returned_at is not None:
        return "returned"
    if loan.due_date < today:
        return "overdue"
    if loan.due_date <= today + timedelta(days=due_soon_days):
        return "due_soon"
    return "active"


def _days_until_due(loan: Loan) -> str:
    if loan.returned_at is not None:
        return ""
    return str((loan.due_date - date.today()).days)


class ExportService:
    def __init__(self, db: Session):
        self.db = db

    def books_csv(self) -> str:
        buffer, writer = _new_csv_buffer()
        writer.writerow(
            [
                "book_id",
                "title",
                "author",
                "genre",
                "year",
                "isbn",
                "edition",
                "unit_price",
                "cover_url",
                "on_hand",
                "min_threshold",
                "aisle",
                "shelf",
                "created_at",
            ]
        )

        books = (
            self.db.query(Book)
            .options(joinedload(Book.inventory).joinedload(Inventory.location))
            .order_by(Book.title.asc(), Book.id.asc())
            .all()
        )

        for book in books:
            inv = book.inventory
            loc = inv.location if inv and inv.location else None

            writer.writerow(
                [
                    book.id,
                    book.title,
                    book.author,
                    book.genre,
                    book.year,
                    book.isbn,
                    book.edition,
                    _money(book.unit_price),
                    book.cover_url or "",
                    "" if inv is None else inv.on_hand,
                    "" if inv is None or inv.min_threshold is None else inv.min_threshold,
                    "" if loc is None else loc.aisle,
                    "" if loc is None else loc.shelf,
                    book.created_at.isoformat(),
                ]
            )

        return buffer.getvalue()

    def members_csv(self) -> str:
        buffer, writer = _new_csv_buffer()
        writer.writerow(
            [
                "member_id",
                "name",
                "email",
                "phone_number",
                "created_at",
            ]
        )

        members = self.db.query(Member).order_by(Member.name.asc(), Member.id.asc()).all()

        for member in members:
            writer.writerow(
                [
                    member.id,
                    member.name,
                    member.email,
                    member.phone_number,
                    member.created_at.isoformat(),
                ]
            )

        return buffer.getvalue()

    def loans_csv(self, *, active_only: bool) -> str:
        buffer, writer = _new_csv_buffer()
        writer.writerow(
            [
                "loan_id",
                "book_id",
                "book_title",
                "isbn",
                "edition",
                "member_id",
                "member_name",
                "member_email",
                "created_at",
                "due_date",
                "returned_at",
                "status",
                "days_until_due",
            ]
        )

        query = (
            self.db.query(Loan)
            .options(joinedload(Loan.book), joinedload(Loan.member))
            .order_by(Loan.due_date.asc(), Loan.id.desc())
        )

        if active_only:
            query = query.filter(Loan.returned_at.is_(None))

        loans = query.all()

        for loan in loans:
            writer.writerow(
                [
                    loan.id,
                    loan.book.id,
                    loan.book.title,
                    loan.book.isbn,
                    loan.book.edition,
                    loan.member.id,
                    loan.member.name,
                    loan.member.email,
                    loan.created_at.isoformat(),
                    loan.due_date.isoformat(),
                    "" if loan.returned_at is None else loan.returned_at.isoformat(),
                    _loan_status(loan),
                    _days_until_due(loan),
                ]
            )

        return buffer.getvalue()

    def sales_csv(self) -> str:
        buffer, writer = _new_csv_buffer()
        writer.writerow(
            [
                "sale_id",
                "sold_at",
                "book_id",
                "book_title",
                "isbn",
                "edition",
                "member_id",
                "member_name",
                "member_email",
                "quantity",
                "unit_price",
                "line_total",
            ]
        )

        sales = (
            self.db.query(Sale)
            .options(joinedload(Sale.book), joinedload(Sale.member))
            .order_by(Sale.sold_at.desc(), Sale.id.desc())
            .all()
        )

        for sale in sales:
            line_total = sale.unit_price * sale.quantity

            writer.writerow(
                [
                    sale.id,
                    sale.sold_at.isoformat(),
                    sale.book.id,
                    sale.book.title,
                    sale.book.isbn,
                    sale.book.edition,
                    "" if sale.member is None else sale.member.id,
                    "" if sale.member is None else sale.member.name,
                    "" if sale.member is None else sale.member.email,
                    sale.quantity,
                    str(sale.unit_price),
                    str(line_total),
                ]
            )

        return buffer.getvalue()
