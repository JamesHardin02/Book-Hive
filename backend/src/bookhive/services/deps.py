from bookhive.db.deps import get_db
from bookhive.repos.user_repo import UserRepo
from bookhive.services.auth_service import AuthService
from fastapi import Depends
from sqlalchemy.orm import Session


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepo(db))
