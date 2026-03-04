from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from bookhive.auth.dependencies import get_current_user
from bookhive.db.deps import get_db
from bookhive.db.models.user import User
from bookhive.repos.location_repo import LocationRepo
from bookhive.schemas.locations import LocationCreate, LocationOut

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=list[LocationOut])
def list_locations(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return LocationRepo(db).list_all()


@router.post("", response_model=LocationOut, status_code=201)
def create_location(
    payload: LocationCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)
):
    return LocationRepo(db).get_or_create(aisle=payload.aisle, shelf=payload.shelf)
