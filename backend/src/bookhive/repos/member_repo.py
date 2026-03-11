from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from book.db.models.member import Member

class MemberRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, member_id: int) -> Optional[Member]:
        return self.db.query(Member).filter(Member.id == member_id).first()

    def get_by_email(self, email: str) -> Optional[Member]:
        return self.db.query(Member).filter(Member.email == email).first()

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
        q: Optional[str],
        name: Optional[str],
        email: Optional[str],
        offset: int,
        limit: int,
    ) -> List[Member]:
        qry = self.db.query(Member)

        if q:
            like = f"%{q}%"
            qry = qry.filter(
                (Member.name.ilike(like)) | (Member.email.ilike(like))
            )
        if name:
            qry = qry.filter(Member.name.ilike(f"%{name}%"))
        if email:
            qry = qry.filter(Member.email.ilike(f"%{email}%"))

        return qry.offset(offset).limit(limit).all()
