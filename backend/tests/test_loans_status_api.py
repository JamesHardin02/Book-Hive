import os
import sys
import unittest
from datetime import date, timedelta

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
from bookhive.db.models.book import Book  # noqa: E402
from bookhive.db.models.inventory import Inventory  # noqa: E402
from bookhive.db.models.loan import Loan  # noqa: E402
from bookhive.db.models.member import Member  # noqa: E402
from bookhive.db.models.user import User  # noqa: E402
from bookhive.main import app  # noqa: E402


class LoanStatusApiTests(unittest.TestCase):
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

            user = User(
                username="manager",
                email="manager@example.com",
                hashed_password="hashed",
                is_active=True,
                is_admin=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            self.token = create_access_token(subject=str(user.id), scope="manager")

            member = Member(
                name="John Doe",
                email="member@example.com",
                phone_number="555-0100",
                created_at=today,
            )
            db.add(member)
            db.commit()
            db.refresh(member)

            book = Book(
                isbn="9780140328721",
                edition=1,
                title="Matilda",
                author="Roald Dahl",
                genre="Fiction",
                year=1988,
            )
            db.add(book)
            db.commit()
            db.refresh(book)

            inventory = Inventory(book_id=book.id, on_hand=10, location_id=None)
            db.add(inventory)
            db.commit()

            loans = [
                Loan(
                    book_id=book.id,
                    member_id=member.id,
                    created_at=today - timedelta(days=10),
                    due_date=today - timedelta(days=1),
                    returned_at=None,
                ),
                Loan(
                    book_id=book.id,
                    member_id=member.id,
                    created_at=today - timedelta(days=2),
                    due_date=today + timedelta(days=3),
                    returned_at=None,
                ),
                Loan(
                    book_id=book.id,
                    member_id=member.id,
                    created_at=today,
                    due_date=today + timedelta(days=20),
                    returned_at=None,
                ),
                Loan(
                    book_id=book.id,
                    member_id=member.id,
                    created_at=today - timedelta(days=12),
                    due_date=today - timedelta(days=4),
                    returned_at=today - timedelta(days=2),
                ),
            ]
            db.add_all(loans)
            db.commit()
        finally:
            db.close()

    def tearDown(self):
        app.dependency_overrides.clear()

    def auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def test_list_loans_includes_derived_statuses(self):
        res = self.client.get(
            "/loans?active_only=false&offset=0&limit=25",
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 200)

        statuses = {item["status"] for item in res.json()}
        self.assertIn("active", statuses)
        self.assertIn("due_soon", statuses)
        self.assertIn("overdue", statuses)
        self.assertIn("returned", statuses)

    def test_due_soon_only_filters_next_seven_days(self):
        res = self.client.get(
            "/loans?due_soon_only=true&due_within_days=7&offset=0&limit=25",
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "due_soon")
        self.assertEqual(data[0]["due_soon"], True)

    def test_overdue_only_filters_correctly(self):
        res = self.client.get(
            "/loans?overdue_only=true&offset=0&limit=25",
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 200)

        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "overdue")

    def test_conflicting_due_filters_return_400(self):
        res = self.client.get(
            "/loans?overdue_only=true&due_soon_only=true&offset=0&limit=25",
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
