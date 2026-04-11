from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from io import StringIO

from bookhive.db.models.book import Book
from bookhive.db.models.inventory import Inventory
from bookhive.db.models.loan import Loan
from bookhive.db.models.sale import Sale
from bookhive.services.settings_service import SettingsService
from sqlalchemy.orm import Session

REPORT_SALES_TRENDS = "sales_trends"
REPORT_CHECKOUTS_BY_GENRE = "checkouts_by_genre"
REPORT_TOP_TITLES = "top_titles"
REPORT_INVENTORY_HEALTH = "inventory_health"


def _new_csv_buffer() -> tuple[StringIO, csv.writer]:
    buffer = StringIO()
    buffer.write("\ufeff")
    return buffer, csv.writer(buffer)


def _as_float(value: Decimal | int | float | None) -> float:
    if value is None:
        return 0.0
    return float(value)


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def _location_label(inv: Inventory) -> str:
    if inv.location is None:
        return "Unassigned"
    return f"{inv.location.aisle}-{inv.location.shelf}"


class ReportingService:
    def __init__(self, db: Session, settings: SettingsService):
        self.db = db
        self.settings = settings

    def _date_window(self, *, days: int) -> tuple[date, date]:
        end = date.today()
        start = end - timedelta(days=max(days - 1, 0))
        return start, end

    def _write_csv(self, *, headers: list[str], rows: list[dict]) -> str:
        buffer, writer = _new_csv_buffer()
        writer.writerow(headers)

        for row in rows:
            writer.writerow([row.get(header, "") for header in headers])

        return buffer.getvalue()

    def sales_trends(self, *, days: int, bucket: str, metric: str) -> dict:
        start, end = self._date_window(days=days)
        sales = (
            self.db.query(Sale)
            .filter(Sale.sold_at >= start)
            .filter(Sale.sold_at <= end)
            .order_by(Sale.sold_at.asc(), Sale.id.asc())
            .all()
        )

        grouped: dict[str, dict] = {}
        total_revenue = 0.0
        total_quantity = 0

        for sale in sales:
            if bucket == "week":
                period_start = sale.sold_at - timedelta(days=sale.sold_at.weekday())
                label = period_start.isoformat()
            else:
                label = sale.sold_at.strftime("%Y-%m")

            if label not in grouped:
                grouped[label] = {
                    "period": label,
                    "revenue": 0.0,
                    "quantity": 0,
                }

            revenue = _as_float(sale.unit_price) * sale.quantity
            grouped[label]["revenue"] += revenue
            grouped[label]["quantity"] += sale.quantity
            total_revenue += revenue
            total_quantity += sale.quantity

        rows = [
            {
                "period": label,
                "revenue": round(data["revenue"], 2),
                "quantity": data["quantity"],
            }
            for label, data in sorted(grouped.items(), key=lambda item: item[0])
        ]

        y_label = "Revenue" if metric == "revenue" else "Units Sold"
        return {
            "report": REPORT_SALES_TRENDS,
            "title": "Sales Trends",
            "description": "Manual sales over time for the selected timeframe.",
            "available_styles": ["bar", "line", "area", "timeline"],
            "default_style": "line",
            "table_columns": ["period", "revenue", "quantity"],
            "detail_columns": [],
            "rows": rows,
            "detail_rows": [],
            "summary": [
                {"label": "Total Revenue", "value": _format_currency(total_revenue)},
                {"label": "Units Sold", "value": str(total_quantity)},
                {"label": "Transactions", "value": str(len(sales))},
            ],
            "empty_message": "No sales were found for the selected timeframe.",
            "chart_meta": {
                "label_field": "period",
                "primary_value_field": metric,
                "secondary_value_field": "quantity" if metric == "revenue" else "revenue",
                "x_title": "Period",
                "y_title": y_label,
            },
        }

    def checkouts_by_genre(self, *, days: int) -> dict:
        start, end = self._date_window(days=days)
        rows = (
            self.db.query(Loan, Book)
            .join(Book, Book.id == Loan.book_id)
            .filter(Loan.created_at >= start)
            .filter(Loan.created_at <= end)
            .all()
        )

        grouped: dict[str, int] = defaultdict(int)
        for loan, book in rows:
            _ = loan
            grouped[book.genre] += 1

        result_rows = [
            {"genre": genre, "loans": total}
            for genre, total in sorted(grouped.items(), key=lambda item: (-item[1], item[0]))
        ]

        top_genre = result_rows[0]["genre"] if result_rows else "—"
        return {
            "report": REPORT_CHECKOUTS_BY_GENRE,
            "title": "Checkouts by Genre",
            "description": "Loan volume grouped by genre for the selected timeframe.",
            "available_styles": ["bar", "donut"],
            "default_style": "bar",
            "table_columns": ["genre", "loans"],
            "detail_columns": [],
            "rows": result_rows,
            "detail_rows": [],
            "summary": [
                {"label": "Loans", "value": str(sum(grouped.values()))},
                {"label": "Genres", "value": str(len(grouped))},
                {"label": "Top Genre", "value": top_genre},
            ],
            "empty_message": "No loan activity was found for the selected timeframe.",
            "chart_meta": {
                "label_field": "genre",
                "primary_value_field": "loans",
                "secondary_value_field": None,
                "x_title": "Genre",
                "y_title": "Loans",
            },
        }

    def top_titles(self, *, days: int, limit: int) -> dict:
        start, end = self._date_window(days=days)
        rows = (
            self.db.query(Loan, Book)
            .join(Book, Book.id == Loan.book_id)
            .filter(Loan.created_at >= start)
            .filter(Loan.created_at <= end)
            .all()
        )

        grouped: dict[tuple[int, str, str, str, int], int] = defaultdict(int)
        for loan, book in rows:
            _ = loan
            title = book.title if book.edition == 1 else f"{book.title} (Ed. {book.edition})"
            grouped[(book.id, title, book.genre, book.isbn, book.edition)] += 1

        ordered = sorted(grouped.items(), key=lambda item: (-item[1], item[0][1]))[:limit]
        result_rows = [
            {
                "title": key[1],
                "genre": key[2],
                "isbn": key[3],
                "edition": key[4],
                "loans": total,
            }
            for key, total in ordered
        ]

        return {
            "report": REPORT_TOP_TITLES,
            "title": "Top Circulated Titles",
            "description": "Most borrowed titles for the selected timeframe.",
            "available_styles": ["bar", "donut"],
            "default_style": "bar",
            "table_columns": ["title", "genre", "isbn", "edition", "loans"],
            "detail_columns": [],
            "rows": result_rows,
            "detail_rows": [],
            "summary": [
                {"label": "Titles Shown", "value": str(len(result_rows))},
                {"label": "Loans", "value": str(sum(item["loans"] for item in result_rows))},
                {
                    "label": "Top Title",
                    "value": result_rows[0]["title"] if result_rows else "—",
                },
            ],
            "empty_message": "No circulation data was found for the selected timeframe.",
            "chart_meta": {
                "label_field": "title",
                "primary_value_field": "loans",
                "secondary_value_field": None,
                "x_title": "Title",
                "y_title": "Loans",
            },
        }

    def inventory_health(self, *, scope: str) -> dict:
        default_threshold = self.settings.get_low_stock_threshold()
        rows = self.db.query(Inventory, Book).join(Book, Book.id == Inventory.book_id).all()

        detail_rows: list[dict] = []
        status_counts = {"stockout": 0, "low_stock": 0, "healthy": 0}
        status_labels = {
            "stockout": "Stockout",
            "low_stock": "Low Stock",
            "healthy": "Healthy",
        }

        for inv, book in rows:
            effective_threshold = (
                inv.min_threshold if inv.min_threshold is not None else default_threshold
            )

            if inv.on_hand == 0:
                status = "stockout"
            elif inv.on_hand <= effective_threshold:
                status = "low_stock"
            else:
                status = "healthy"

            status_counts[status] += 1

            if scope == "attention_only" and status == "healthy":
                continue

            detail_rows.append(
                {
                    "title": book.title,
                    "isbn": book.isbn,
                    "genre": book.genre,
                    "status": status,
                    "status_display": status_labels[status],
                    "on_hand": inv.on_hand,
                    "threshold": effective_threshold,
                    "location": _location_label(inv),
                }
            )

        detail_rows.sort(key=lambda row: (row["on_hand"], row["title"]))
        chart_rows = []
        for status in ("stockout", "low_stock", "healthy"):
            if scope == "attention_only" and status == "healthy":
                continue
            chart_rows.append(
                {
                    "status": status,
                    "label": status_labels[status],
                    "count": status_counts[status],
                }
            )

        return {
            "report": REPORT_INVENTORY_HEALTH,
            "title": "Inventory Health",
            "description": "Current stock posture based on on-hand counts and threshold rules.",
            "available_styles": ["bar", "donut"],
            "default_style": "donut",
            "table_columns": ["label", "count"],
            "detail_columns": [
                "title",
                "isbn",
                "genre",
                "status_display",
                "on_hand",
                "threshold",
                "location",
            ],
            "rows": chart_rows,
            "detail_rows": detail_rows,
            "summary": [
                {"label": "Stockout Titles", "value": str(status_counts["stockout"])},
                {"label": "Low Stock Titles", "value": str(status_counts["low_stock"])},
                {"label": "Healthy Titles", "value": str(status_counts["healthy"])},
            ],
            "empty_message": "No inventory rows are available for the current report.",
            "chart_meta": {
                "label_field": "label",
                "primary_value_field": "count",
                "secondary_value_field": None,
                "x_title": "Status",
                "y_title": "Titles",
            },
        }

    def export_csv(
        self,
        *,
        report: str,
        days: int,
        bucket: str,
        metric: str,
        limit: int,
        scope: str,
    ) -> str:
        if report == REPORT_SALES_TRENDS:
            data = self.sales_trends(days=days, bucket=bucket, metric=metric)
            return self._write_csv(headers=data["table_columns"], rows=data["rows"])

        if report == REPORT_CHECKOUTS_BY_GENRE:
            data = self.checkouts_by_genre(days=days)
            return self._write_csv(headers=data["table_columns"], rows=data["rows"])

        if report == REPORT_TOP_TITLES:
            data = self.top_titles(days=days, limit=limit)
            return self._write_csv(headers=data["table_columns"], rows=data["rows"])

        if report == REPORT_INVENTORY_HEALTH:
            data = self.inventory_health(scope=scope)
            return self._write_csv(headers=data["detail_columns"], rows=data["detail_rows"])

        raise ValueError("Unsupported report")
