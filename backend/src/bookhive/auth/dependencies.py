from bookhive.auth.security import decode_token
from bookhive.db.deps import get_db
from bookhive.repos.user_repo import UserRepo
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

COOKIE_NAME = "access_token"


def _get_token(request: Request, header_token: str | None) -> str:
    if header_token:
        return header_token
    cookie_token = request.cookies.get(COOKIE_NAME)
    if cookie_token:
        return cookie_token
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    header_token: str | None = Depends(oauth2_scheme),
):
    token = _get_token(request, header_token)

    try:
        payload = decode_token(token)
        subject = payload.get("sub")
        scope = payload.get("scope")
        if subject is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        if scope != "manager":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient scope")

    except JWTError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from ex

    repo = UserRepo(db)
    user = repo.get_by_id(int(subject))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")
    return user


def require_admin_user(current_user=Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return current_user
