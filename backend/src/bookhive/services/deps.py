from bookhive.db.deps import get_db
from bookhive.repos.book_repo import BookRepo
from bookhive.repos.inventory_repo import InventoryRepo
from bookhive.repos.location_repo import LocationRepo
from bookhive.repos.metadata_cache_repo import MetadataCacheRepo
from bookhive.repos.settings_repo import SettingsRepo
from bookhive.repos.stock_adjustment_repo import StockAdjustmentRepo
from bookhive.repos.user_repo import UserRepo
from bookhive.repos.member_repo import MemberRepo
from bookhive.services.auth_service import AuthService
from bookhive.services.book_service import BookService
from bookhive.services.dashboard_service import DashboardService
from bookhive.services.inventory_service import InventoryService
from bookhive.services.openlibrary_service import OpenLibraryService
from bookhive.services.settings_service import SettingsService
from bookhive.services.member_service import MemberService
from fastapi import Depends
from sqlalchemy.orm import Session


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepo(db))


def get_book_service(db: Session = Depends(get_db)) -> BookService:
    return BookService(BookRepo(db), InventoryRepo(db), LocationRepo(db))


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    return InventoryService(InventoryRepo(db), LocationRepo(db), StockAdjustmentRepo(db))


def get_openlibrary_service(db: Session = Depends(get_db)) -> OpenLibraryService:
    return OpenLibraryService(MetadataCacheRepo(db))


def get_settings_service(db: Session = Depends(get_db)) -> SettingsService:
    return SettingsService(SettingsRepo(db))


def get_dashboard_service(
    db: Session = Depends(get_db),
    settings: SettingsService = Depends(get_settings_service),
) -> DashboardService:
    return DashboardService(db, settings)

def get_member_service(db: Session = Depends(get_db)) -> MemberService:
    return MemberService(MemberRepo(db))