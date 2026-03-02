import os
import sys
import unittest
import logging

logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Ensure imports work when running from repo root or backend/
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)


from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from bookhive.db.base import Base  # noqa: E402
from bookhive.db.deps import get_db  # noqa: E402
from bookhive.main import app  # noqa: E402


class AuthCookieFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Prevent app startup from touching real MySQL engine during tests
        os.environ["BOOKHIVE_ENV"] = "test"
        os.environ["BOOKHIVE_COOKIE_SECURE"] = "false"
        os.environ["JWT_SECRET_KEY"] = "test-secret"
        os.environ["JWT_ALGORITHM"] = "HS256"
        os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

        # In-memory SQLite shared across threads/connections
        cls.engine = create_engine(
            "sqlite+pysqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.TestingSessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=cls.engine
        )

        Base.metadata.drop_all(bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        def override_get_db():
            db = self.TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_cookie_login_me_logout_flow(self):
        # Register
        reg = self.client.post(
            "/auth/register",
            json={
                "username": "cookieuser",
                "email": "cookie@example.com",
                "password": "secret123",
            },
        )
        self.assertEqual(reg.status_code, 201)

        # Login (sets cookie)
        token_res = self.client.post(
            "/auth/token",
            data={"username": "cookie@example.com", "password": "secret123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(token_res.status_code, 200)

        set_cookie = token_res.headers.get("set-cookie", "")
        self.assertIn("access_token=", set_cookie)
        self.assertIn("HttpOnly", set_cookie)  # important security property

        # /me WITHOUT Authorization header (cookie should be automatically stored by TestClient)
        me = self.client.get("/auth/me")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], "cookie@example.com")

        # Logout clears cookie
        out = self.client.post("/auth/logout")
        self.assertEqual(out.status_code, 200)
        cleared = out.headers.get("set-cookie", "")
        self.assertIn("access_token=", cleared)
        self.assertTrue(("Max-Age=0" in cleared) or ("expires=" in cleared.lower()))

        # /me should now fail (cookie removed)
        me2 = self.client.get("/auth/me")
        self.assertIn(me2.status_code, (401, 403))

    def test_me_requires_auth(self):
        me = self.client.get("/auth/me")
        self.assertEqual(me.status_code, 401)


if __name__ == "__main__":
    unittest.main()
