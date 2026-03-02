import os
import sys
import unittest
import logging

logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from bookhive.db.base import Base  # noqa: E402
from bookhive.db.deps import get_db  # noqa: E402
from bookhive.main import app  # noqa: E402
from bookhive.db.models.user import User  # noqa: E402
from bookhive.auth.security import hash_password  # noqa: E402


class AuthApiErrorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["BOOKHIVE_ENV"] = "test"
        os.environ["JWT_SECRET_KEY"] = "test-secret"
        os.environ["JWT_ALGORITHM"] = "HS256"
        os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
        os.environ["BOOKHIVE_COOKIE_SECURE"] = "false"

        cls.engine = create_engine(
            "sqlite+pysqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

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

        # seed a user directly (bypassing register validation concerns)
        db = self.SessionLocal()
        try:
            db.query(User).delete()
            db.commit()
            u = User(
                username="apiuser",
                email="apiuser@example.com",
                hashed_password=hash_password("RightPassword!"),
                is_active=True,
                is_admin=True,
            )
            db.add(u)
            db.commit()
        finally:
            db.close()

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_token_invalid_password_returns_401(self):
        res = self.client.post(
            "/auth/token",
            data={"username": "apiuser@example.com", "password": "WrongPassword!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(res.status_code, 401)

    def test_token_inactive_user_returns_403(self):
        # mark inactive
        db = self.SessionLocal()
        try:
            u = db.query(User).filter(User.email == "apiuser@example.com").first()
            u.is_active = False
            db.commit()
        finally:
            db.close()

        res = self.client.post(
            "/auth/token",
            data={"username": "apiuser@example.com", "password": "RightPassword!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(res.status_code, 403)

    def test_logout_without_login_is_ok(self):
        # should be safe/idempotent
        res = self.client.post("/auth/logout")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json().get("ok"), True)


if __name__ == "__main__":
    unittest.main()