from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, List

def _normalize_phone(s: str) -> str:
    return "".join(ch for ch in s if ch.isdigit())

class MemberCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> Optional[str]:
        if v is None:
            return None
        digits = _normalize_phone(v)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must have between 7 and 15 digits")
        return digits

class MemberCreate(MemberBase):
    pass

class MemberUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> Optional[str]:
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
    phone: Optional[str] = None
    address: Optional[str] = None

class MemberSearchResult(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[MemberOut]