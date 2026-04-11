import os
import sys
import unittest
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

os.environ["BOOKHIVE_ENV"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from bookhive.auth.security import create_access_token  # noqa: E402
from bookhive.db.base import Base  # noqa: E402
from bookhive.db.deps import get_db  # noqa: E402
from bookhive.db.models.app_setting import AppSetting  # noqa: E402
from bookhive.db.models.book import Book  # noqa: E402
from bookhive.db.models.inventory import Inventory  # noqa: E402
from bookhive.db.models.loan import Loan  # noqa: E402
from bookhive.db.models.location import Location  # noqa: E402
from bookhive.db.models.member import Member  # noqa: E402
from bookhive.db.models.sale import Sale  # noqa: E402
from bookhive.db.models.user import User  # noqa: E402
from bookhive.main import app  # noqa: E402


class ReportsApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(
            "sqlite+pysqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.engine
        )
        Base.metadata.drop_all(bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        def override_get_db():
            db = self.SessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

        db = self.SessionLocal()
        try:
            today = date.today()

            manager = User(
                username="manager",
                email="manager@example.com",
                hashed_password="hashed",
                is_active=True,
                is_admin=True,
            )
            db.add(manager)
            db.commit()
            db.refresh(manager)
            self.token = create_access_token(subject=str(manager.id), scope="manager")

            db.add(AppSetting(key="low_stock_threshold", int_value=3))
            db.commit()

            location = Location(aisle="A", shelf="1")
            db.add(location)
            db.commit()
            db.refresh(location)

            member = Member(
                name="John Doe",
                email="john@example.com",
                phone_number="555-1000",
                created_at=today - timedelta(days=30),
            )
            db.add(member)
            db.commit()
            db.refresh(member)

            books = [
                Book(
                    isbn="9780140328721",
                    edition=1,
                    title="Matilda",
                    author="Roald Dahl",
                    genre="Children's",
                    year=1988,
                    unit_price=Decimal("8.99"),
                ),
                Book(
                    isbn="9780451524935",
                    edition=1,
                    title="1984",
                    author="George Orwell",
                    genre="Fiction",
                    year=1949,
                    unit_price=Decimal("9.99"),
                ),
                Book(
                    isbn="9780062316094",
                    edition=1,
                    title="Sapiens",
                    author="Yuval Noah Harari",
                    genre="History",
                    year=2011,
                    unit_price=Decimal("18.99"),
                ),
            ]
            db.add_all(books)
            db.commit()
            for book in books:
                db.refresh(book)

            inventories = [
                Inventory(
                    book_id=books[0].id,
                    on_hand=0,
                    location_id=location.id,
                    min_threshold=2,
                ),
                Inventory(
                    book_id=books[1].id,
                    on_hand=2,
                    location_id=location.id,
                    min_threshold=3,
                ),
                Inventory(
                    book_id=books[2].id,
                    on_hand=8,
                    location_id=location.id,
                    min_threshold=2,
                ),
            ]
            db.add_all(inventories)

            loans = [
                Loan(
                    book_id=books[0].id,
                    member_id=member.id,
                    created_at=today - timedelta(days=10),
                    due_date=today + timedelta(days=4),
                    returned_at=None,
                ),
                Loan(
                    book_id=books[1].id,
                    member_id=member.id,
                    created_at=today - timedelta(days=7),
                    due_date=today + timedelta(days=12),
                    returned_at=None,
                ),
                Loan(
                    book_id=books[1].id,
                    member_id=member.id,
                    created_at=today - timedelta(days=4),
                    due_date=today + timedelta(days=18),
                    returned_at=None,
                ),
            ]
            db.add_all(loans)

            sales = [
                Sale(
                    book_id=books[0].id,
                    member_id=member.id,
                    quantity=2,
                    unit_price=Decimal("8.99"),
                    sold_at=today - timedelta(days=40),
                ),
                Sale(
                    book_id=books[1].id,
                    member_id=None,
                    quantity=1,
                    unit_price=Decimal("9.99"),
                    sold_at=today - timedelta(days=15),
                ),
            ]
            db.add_all(sales)
            db.commit()
        finally:
            db.close()

    def tearDown(self):
        app.dependency_overrides.clear()

    def auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def test_sales_trends_returns_plotly_ready_rows(self):
        res = self.client.get(
            "/reports/sales-trends?days=365&bucket=month&metric=revenue",
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["report"], "sales_trends")
        self.assertGreaterEqual(len(data["rows"]), 1)
        self.assertIn("line", data["available_styles"])

    def test_checkouts_by_genre_groups_counts(self):
        res = self.client.get(
            "/reports/checkouts-by-genre?days=365",
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 200)
        rows = res.json()["rows"]
        grouped = {row["genre"]: row["loans"] for row in rows}
        self.assertEqual(grouped.get("Fiction"), 2)
        self.assertEqual(grouped.get("Children's"), 1)

    def test_top_titles_honors_limit(self):
        res = self.client.get(
            "/reports/top-titles?days=365&limit=1",
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 200)
        rows = res.json()["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "1984")

    def test_inventory_health_returns_detail_rows(self):
        res = self.client.get(
            "/reports/inventory-health?scope=attention_only",
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["report"], "inventory_health")
        self.assertTrue(any(row["status"] == "stockout" for row in data["detail_rows"]))
        self.assertTrue(
            any(row["status"] == "low_stock" for row in data["detail_rows"])
        )

    def test_export_csv_returns_headers(self):
        res = self.client.get(
            "/reports/export.csv?report=inventory_health&scope=attention_only",
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 200)
        content = res.text
        self.assertIn(
            "title,isbn,genre,status_display,on_hand,threshold,location", content
        )


if __name__ == "__main__":
    unittest.main()
