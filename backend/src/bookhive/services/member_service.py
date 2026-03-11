from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from bookhive.db.models.member import Member
from bookhive.repos.member_repo import MemberRepo

def _normalize_phone(phone: str) -> str:
    return " ".join(ch for ch in s if ch.isdigit())

class MemberService:
    def __init__(self, member_repo: MemberRepo):
        self.member_repo = member_repo

    def create_member(
        self,
        *,
        name: str,
        email: str,
        phone_number: str,
    ) -> Member:
        # Email uniqueness check
        existing = self.member_repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{email}' is already in use",
            )

        normalized_phone = _normalize_phone(phone_number)

        member = Member(
            name=name,
            email=email,
            phone_number=normalized_phone,
        )

        return self.member_repo.create(member)

    def get_member(self, *, member_id: int) -> Member:
        member = self.member_repo.get_by_id(member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )
        return member

    def update_member(
        self,
        *,
        member_id: int,
        name: str | None = None,
        email: str | None = None,
        phone_number: str | None = None,
    ) -> Member:
        member = self.member_repo.get_by_id(member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )

        # Email uniqueness check
        if email is not None:
            existing = self.member_repo.get_by_email(email)
            if existing and existing.id != member.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email '{email}' is already in use",
                )
            member.email = email

        if name is not None:
            member.name = name

        if phone_number is not None:
            member.phone_number = _normalize_phone(phone_number)

        # Commit update
        self.member_repo.db.commit()
        self.member_repo.db.refresh(member)
        return member

    def search_members(
        self,
        *,
        q: str,
        offset: int,
        limit: int,
    ) -> list[Member]:
        return self.member_repo.search(
            q=q,
            offset=offset,
            limit=limit,
        )

    def count_members(self, *, q: str) -> int:
        return self.member_repo.count(q)

    
     