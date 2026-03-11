from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _normalize_phone(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())


class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = None
    address: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str | None:
        if v is None:
            return None
        digits = _normalize_phone(v)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must have between 7 and 15 digits")
        return digits


class MemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str | None:
        if v is None:
            return None
        digits = _normalize_phone(v)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must have between 7 and 15 digits")
        return digits


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: str | None = None
    address: str | None = None


class MemberSearchResult(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[MemberOut]
