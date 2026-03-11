from fastapi import APIRouter, Depends, HTTPException, Query

from bookhive.auth.dependencies import get_current_user
from bookhive.db.models.user import User
from bookhive.schemas.members import MemberCreate, MemberOut, MemberUpdate, MemberSearchResult
from bookhive.services.members_service import MemberService
from bookhive.services.deps import get_member_service

router = APIRouter(prefix="/members", tags=["members"])

@router.post("/", response_model=MemberOut, status_code=201)
def create_member(
    payload: MemberCreate,
    svc: MemberService = Depends(get_member_service),
    _: User = Depends(get_current_user),
):
    member = svc.create_member(
        name=payload.name,
        email=payload.email,
        phone_number=payload.phone_number,
    )
    return MemberOut.model_validate(member)

@router.get("/{member_id}", response_model=MemberOut)
def get_member(
    member_id: int,
    svc: MemberService = Depends(get_member_service)
    _: User = Depends(get_current_user),
):
    member = svc.get_member(member_id)
    return MemberOut.model_validate(member)

@router.patch("/{member_id}", response_model=MemberOut)
def update_member(
    member_id: int,
    payload: MemberUpdate,
    svc: MemberService = Depends(get_member_service),
    _: User = Depends(get_current_user),
):
    member = svc.update_member(
        member_id=member_id,
        **payload.model_dump(exclude_unset=True),
    )
    return MemberOut.model_validate(member)

@router.get("/search", response_model=MemberSearchResult)
def search_members(
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    svc: MemberService = Depends(get_member_service),
    _: User = Depends(get_current_user),
):
    offset = (page - 1) * page_size

    results = svc.search_members(q=q or " ", offset=offset, limit=page_size)
    total = svc.count_members(q=q or " ")

    return MemberSearchResult(
        total=total,
        page=page,
        page_size=page_size,
        results=[MemberOut.model_validate(m) for m in results],
    )