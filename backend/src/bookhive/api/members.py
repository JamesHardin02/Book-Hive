from fastapi import APIRouter, Depends, Query

from bookhive.auth.dependencies import get_current_user
from bookhive.db.models.user import User
from bookhive.schemas.members import MemberCreate, MemberOut, MemberUpdate
from bookhive.services.deps import get_member_service
from bookhive.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=MemberOut, status_code=201)
def create_member(
    payload: MemberCreate,
    svc: MemberService = Depends(get_member_service),
    _: User = Depends(get_current_user),
):
    return svc.create_member(
        name=payload.name,
        email=payload.email,
        phone_number=payload.phone_number,
    )


@router.get("/{member_id}", response_model=MemberOut)
def get_member(
    member_id: int,
    svc: MemberService = Depends(get_member_service),
    _: User = Depends(get_current_user),
):
    return svc.get_member(member_id=member_id)


@router.get("", response_model=list[MemberOut])
def list_members(
    name: str | None = None,
    email: str | None = None,
    phone_number: str | None = Query(default=None),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    svc: MemberService = Depends(get_member_service),
    _: User = Depends(get_current_user),
):
    return svc.list_members(
        name=name,
        email=email,
        phone_number=phone_number,
        offset=offset,
        limit=limit,
    )


@router.patch("/{member_id}", response_model=MemberOut)
def update_member(
    member_id: int,
    payload: MemberUpdate,
    svc: MemberService = Depends(get_member_service),
    _: User = Depends(get_current_user),
):
    return svc.update_member(member_id=member_id, **payload.model_dump(exclude_unset=True))


@router.delete("/{member_id}", status_code=204)
def delete_member(
    member_id: int,
    svc: MemberService = Depends(get_member_service),
    _: User = Depends(get_current_user),
):
    svc.delete_member(member_id=member_id)
    return None
