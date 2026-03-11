from __future__ import annotations

from bookhive.db.models.member import Member
from sqlalchemy.orm import Session


class MemberRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, member_id: int) -> Member | None:
        return self.db.query(Member).filter(Member.id == member_id).first()

    def create(self, member: Member) -> Member:
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def delete(self, member: Member) -> None:
        self.db.delete(member)
        self.db.commit()

    def list_search(
        self,
        *,
        name: str | None,
        email: str | None,
        phone_number: str | None,
        offset: int,
        limit: int,
    ) -> list[Member]:
        qry = self.db.query(Member)

        if name:
            qry = qry.filter(Member.name.ilike(f"%{name}%"))
        if email:
            qry = qry.filter(Member.email.ilike(f"%{email}%"))
        if phone_number:
            qry = qry.filter(Member.phone_number.ilike(f"%{phone_number}%"))

        return qry.order_by(Member.name.asc()).offset(offset).limit(limit).all()
