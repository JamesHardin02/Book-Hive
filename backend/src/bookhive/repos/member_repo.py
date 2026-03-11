from bookhive.db.models.member import Member
from sqlalchemy.orm import Session


class MemberRepo:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> Member | None:
        print("get all repo function hit")
        print(self.db.query(Member).first())
        return self.db.query(Member).first()

    def get_by_id(self, member_id: int) -> Member | None:
        return self.db.query(Member).filter(Member.id == member_id).first()

    def get_by_email(self, email: str) -> Member | None:
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
        q: str | None,
        name: str | None,
        email: str | None,
        offset: int,
        limit: int,
    ) -> list[Member]:
        qry = self.db.query(Member)

        if q:
            like = f"%{q}%"
            qry = qry.filter((Member.name.ilike(like)) | (Member.email.ilike(like)))
        if name:
            qry = qry.filter(Member.name.ilike(f"%{name}%"))
        if email:
            qry = qry.filter(Member.email.ilike(f"%{email}%"))

        return qry.offset(offset).limit(limit).all()
