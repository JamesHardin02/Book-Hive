import os
import sys
import unittest
from dataclasses import dataclass

# Ensure imports work when running from repo root or backend/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Ensure token settings are stable for tests
os.environ["BOOKHIVE_ENV"] = "test"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"

from bookhive.auth.security import decode_token, verify_password  # noqa: E402
from bookhive.services.auth_service import AuthService  # noqa: E402
from bookhive.services.errors import (  # noqa: E402
    EmailAlreadyRegistered,
    InactiveUser,
    InvalidCredentials,
)


@dataclass
class FakeUser:
    id: int
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = True


class FakeUserRepo:
    """
    Fake repo that behaves like UserRepo, but stores users in-memory.
    """

    def __init__(self):
        self._users_by_id: dict[int, FakeUser] = {}
        self._users_by_email: dict[str, FakeUser] = {}
        self._next_id = 1

    def get_by_email(self, email: str):
        return self._users_by_email.get(email)

    def get_by_id(self, user_id: int):
        return self._users_by_id.get(user_id)

    def create(self, *, username: str, email: str, hashed_password: str):
        user = FakeUser(
            id=self._next_id,
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
        )
        self._next_id += 1
        self._users_by_id[user.id] = user
        self._users_by_email[user.email] = user
        return user


class AuthServiceUnitTests(unittest.TestCase):
    def setUp(self):
        self.repo = FakeUserRepo()
        self.svc = AuthService(self.repo)

    def test_register_user_success_hashes_password(self):
        user = self.svc.register_user(username="alice", email="alice@example.com", password="Secret123!")

        self.assertEqual(user.email, "alice@example.com")
        self.assertNotEqual(user.hashed_password, "Secret123!")
        self.assertTrue(verify_password("Secret123!", user.hashed_password))

    def test_register_user_duplicate_email_raises(self):
        self.svc.register_user(username="a", email="dup@example.com", password="Secret123!")
        with self.assertRaises(EmailAlreadyRegistered):
            self.svc.register_user(username="b", email="dup@example.com", password="Secret123!")

    def test_authenticate_invalid_email_raises(self):
        with self.assertRaises(InvalidCredentials):
            self.svc.authenticate(email="missing@example.com", password="pw")

    def test_authenticate_invalid_password_raises(self):
        self.svc.register_user(username="bob", email="bob@example.com", password="RightPassword!")
        with self.assertRaises(InvalidCredentials):
            self.svc.authenticate(email="bob@example.com", password="WrongPassword!")

    def test_authenticate_inactive_user_raises(self):
        user = self.svc.register_user(username="carol", email="carol@example.com", password="Secret123!")
        # force inactive in fake storage
        user.is_active = False

        with self.assertRaises(InactiveUser):
            self.svc.authenticate(email="carol@example.com", password="Secret123!")

    def test_issue_token_contains_scope_manager(self):
        user = self.svc.register_user(username="dave", email="dave@example.com", password="Secret123!")
        token = self.svc.issue_token(user_id=user.id)

        payload = decode_token(token)
        self.assertEqual(payload["sub"], str(user.id))
        self.assertEqual(payload.get("scope"), "manager")


if __name__ == "__main__":
    unittest.main()