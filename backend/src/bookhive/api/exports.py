from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from bookhive.auth.dependencies import get_current_user
from bookhive.db.models.user import User
from bookhive.services.deps import get_export_service
from bookhive.services.export_service import ExportService

router = APIRouter(prefix="/exports", tags=["exports"])


def _csv_response(filename: str, content: str) -> Response:
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/books.csv")
def export_books(
    svc: ExportService = Depends(get_export_service),
    _: User = Depends(get_current_user),
):
    return _csv_response("books.csv", svc.books_csv())


@router.get("/members.csv")
def export_members(
    svc: ExportService = Depends(get_export_service),
    _: User = Depends(get_current_user),
):
    return _csv_response("members.csv", svc.members_csv())


@router.get("/loans.csv")
def export_loans(
    active_only: bool = Query(False),
    svc: ExportService = Depends(get_export_service),
    _: User = Depends(get_current_user),
):
    filename = "loans_active.csv" if active_only else "loans.csv"
    return _csv_response(filename, svc.loans_csv(active_only=active_only))


@router.get("/sales.csv")
def export_sales(
    svc: ExportService = Depends(get_export_service),
    _: User = Depends(get_current_user),
):
    return _csv_response("sales.csv", svc.sales_csv())
