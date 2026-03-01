from __future__ import annotations

from bookhive.auth.security import create_access_token, hash_password, verify_password
from bookhive.repos.user_repo import UserRepo
from bookhive.services.errors import EmailAlreadyRegistered, InactiveUser, InvalidCredentials


class AuthService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def register_user(self, *, username: str, email: str, password: str):
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise EmailAlreadyRegistered()

        return self.user_repo.create(
            username=username, email=email, hashed_password=hash_password(password)
        )

    def authenticate(self, *, email: str, password: str):
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        if not user.is_active:
            raise InactiveUser()

        return user

    def issue_token(self, *, user_id: int) -> str:
        return create_access_token(subject=str(user_id), scope="manager")
