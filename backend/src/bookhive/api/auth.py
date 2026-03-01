import os

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from bookhive.auth.dependencies import get_current_user
from bookhive.auth.schemas import Token, UserCreate, UserPublic
from bookhive.services.auth_service import AuthService
from bookhive.services.deps import get_auth_service
from bookhive.services.errors import EmailAlreadyRegistered, InactiveUser, InvalidCredentials

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_NAME = "access_token"


def _cookie_setting() -> dict:
    # For localhost dev, Secure must be false for http usage
    # In prod for https usage, set BOOKHIVE_COOKIE_SECURE=true
    secure = os.getenv("BOOKHIVE_COOKIE_SECURE", "false").lower() in ("1", "true", "yes")
    return {
        "httponly": True,
        "secure": secure,
        "samesite": "lax",
        "path": "/",
    }


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, svc: AuthService = Depends(get_auth_service)):
    try:
        return svc.register_user(
            username=payload.username, email=payload.email, password=payload.password
        )
    except EmailAlreadyRegistered:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        ) from exec


@router.post("/token", response_model=Token)
def login(
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    svc: AuthService = Depends(get_auth_service),
) -> Token:
    # OAuth2 form uses 'username' field; treat email as usernam
    try:
        user = svc.authenticate(email=form.username, password=form.password)
        token = svc.issue_token(user_id=user.id)
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials"
        ) from exec
    except InactiveUser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive") from exec

    response.set_cookie(COOKIE_NAME, token, **_cookie_setting())


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserPublic)
def me(current_user=Depends(get_current_user)):
    return current_user
