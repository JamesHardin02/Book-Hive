import dns.resolver
from pydantic import BaseModel, EmailStr, Field, field_validator


def domain_has_mx(domain: str) -> bool:
    try:
        dns.resolver.resolve(domain, "MX")
        return True
    except Exception as e:
        print(e)
        return False


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)

    @field_validator("email")
    def validate_tld(cls, email_value):
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
