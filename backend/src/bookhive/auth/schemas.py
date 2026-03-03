import os

import dns.resolver
from pydantic import BaseModel, EmailStr, Field, field_validator


def domain_has_mx(domain: str) -> bool:
    try:
        dns.resolver.resolve(domain, "MX")
        return True
    except Exception:
        return False


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)

    @field_validator("email")
    def validate_tld(cls, email_value: str):
        # Skip MX check during automated tests to avoid dns issues
        if os.getenv("BOOKHIVE_ENV") == "test":
            return email_value

        # Explicitly activate email MX checks, otherwise just return email_value
        if os.getenv("EMAIL_MX_CHECK", "false").lower() not in ("1", "true", "yes"):
            return email_value

        domain = email_value.split("@")[1]
        if not domain_has_mx(domain):
            raise ValueError("Email domain does not accept mail")
        return email_value


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool

    class Config:
        from_attributes = True
