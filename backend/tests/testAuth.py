import unittest

import os
import sys

import logging

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from bookhive.main import app
from bookhive.db.deps import get_db
from bookhive.db.base import Base
from bookhive.db.models.user import User
from bookhive.auth.dependencies import get_current_user

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

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

    def setUp(self):
        self.db = TestingSessionLocal()

        def override_get_db():
            try:
                yield self.db
            finally:
                pass

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        engine.dispose()

    def tearDown(self):
        self.db.close()
        app.dependency_overrides.clear()

    def test_register_success(self):
        response = self.client.post(
            "/auth/register",
            json={"email": "alice@example.com", "password": "secret123"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "alice@example.com")

    def test_register_duplicate(self):
        self.client.post(
            "/auth/register",
            json={"email": "dup@example.com", "password": "secret123"},
        )

        response = self.client.post(
            "/auth/register",
            json={"email": "dup@example.com", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Email already registered")

    def test_login_success(self):
        self.client.post(
            "/auth/register",
            json={"email": "bob@example.com", "password": "pw12345"},
        )

        response = self.client.post(
            "/auth/token",
            data={"username": "bob@example.com", "password": "pw12345"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_me_with_override(self):
        user = User(email="me@example.com", hashed_password="fake")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        def override_get_current_user():
            return user

        app.dependency_overrides[get_current_user] = override_get_current_user

        response = self.client.get("/auth/me")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["email"], "me@example.com")


if __name__ == "__main__":
    unittest.main()
