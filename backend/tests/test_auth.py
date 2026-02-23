import os
import sys
import unittest
import logging

logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Ensure imports work when running from repo root or backend/
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

# Prevent app startup from touching the real MySQL engine during tests
os.environ["BOOKHIVE_ENV"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from bookhive.db.base import Base  # noqa: E402
from bookhive.db.deps import get_db  # noqa: E402
from bookhive.main import app  # noqa: E402

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_auth.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class AuthTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def setUp(self):
        db = TestingSessionLocal()

        def override_get_db():
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_register_success(self):
        response = self.client.post(
            "/auth/register",
            json={
                "username": "JohnDoe",
                "email": "johndoe@gmail.com",
                "password": "secret123",
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "johndoe@gmail.com")
        self.assertEqual(response.json()["username"], "JohnDoe")

    def test_register_duplicate_email(self):
        self.client.post(
            "/auth/register",
            json={
                "username": "dup1",
                "email": "dup@example.com",
                "password": "secret123",
            },
        )

        response = self.client.post(
            "/auth/register",
            json={
                "username": "dup2",
                "email": "dup@example.com",
                "password": "secret123",
            },
        )

        self.assertEqual(response.status_code, 409)

    def test_login_and_me(self):
        # Register user
        self.client.post(
            "/auth/register",
            json={
                "username": "bob",
                "email": "bob@example.com",
                "password": "pw123456",
            },
        )

        # Login. NOTE: backend currently treats OAuth2 "username" field as EMAIL in auth.py.
        # If login ever authenticates by username, update this accordingly.
        token_res = self.client.post(
            "/auth/token",
            data={"username": "bob@example.com", "password": "pw123456"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(token_res.status_code, 200)
        token = token_res.json()["access_token"]

        # Call /me with Bearer token
        me_res = self.client.get(
            "/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["email"], "bob@example.com")


if __name__ == "__main__":
    unittest.main()
