from __future__ import annotations

from datetime import date

from bookhive.db.models.member import Member
from bookhive.repos.member_repo import MemberRepo
from fastapi import HTTPException, status


class MemberService:
    def __init__(self, repo: MemberRepo):
        self.repo = repo

    def create_member(self, *, name: str, email: str, phone_number: str) -> Member:
        member = Member(
            name=name,
            email=email,
            phone_number=phone_number,
            created_at=date.today(),
        )
        return self.repo.create(member)

    def get_member(self, *, member_id: int) -> Member:
        member = self.repo.get_by_id(member_id)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        return member

    def list_members(
        self,
        *,
        name: str | None,
        email: str | None,
        phone_number: str | None,
        offset: int,
        limit: int,
    ) -> list[Member]:
        return self.repo.list_search(
            name=name,
            email=email,
            phone_number=phone_number,
            offset=offset,
            limit=limit,
        )

    def update_member(self, *, member_id: int, **fields) -> Member:
        member = self.repo.get_by_id(member_id)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

        for key, value in fields.items():
            if value is not None:
                setattr(member, key, value)

        self.repo.db.commit()
        self.repo.db.refresh(member)
        return member

    def delete_member(self, *, member_id: int) -> None:
        member = self.repo.get_by_id(member_id)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        self.repo.delete(member)
