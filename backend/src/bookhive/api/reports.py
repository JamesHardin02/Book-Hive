from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from bookhive.auth.dependencies import get_current_user
from bookhive.db.models.user import User
from bookhive.services.deps import get_reporting_service
from bookhive.services.reporting_service import (
    REPORT_CHECKOUTS_BY_GENRE,
    REPORT_INVENTORY_HEALTH,
    REPORT_SALES_TRENDS,
    REPORT_TOP_TITLES,
    ReportingService,
)

router = APIRouter(prefix="/reports", tags=["reports"])


def _csv_response(filename: str, content: str) -> Response:
    return Response(
        content=content,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/sales-trends")
def sales_trends(
    days: int = Query(365, ge=1, le=3650),
    bucket: str = Query("month", pattern="^(week|month)$"),
    metric: str = Query("revenue", pattern="^(revenue|quantity)$"),
    svc: ReportingService = Depends(get_reporting_service),
    _: User = Depends(get_current_user),
):
    return svc.sales_trends(days=days, bucket=bucket, metric=metric)


@router.get("/checkouts-by-genre")
def checkouts_by_genre(
    days: int = Query(90, ge=1, le=3650),
    svc: ReportingService = Depends(get_reporting_service),
    _: User = Depends(get_current_user),
):
    return svc.checkouts_by_genre(days=days)


@router.get("/top-titles")
def top_titles(
    days: int = Query(90, ge=1, le=3650),
    limit: int = Query(10, ge=1, le=25),
    svc: ReportingService = Depends(get_reporting_service),
    _: User = Depends(get_current_user),
):
    return svc.top_titles(days=days, limit=limit)


@router.get("/inventory-health")
def inventory_health(
    scope: str = Query("all", pattern="^(all|attention_only)$"),
    svc: ReportingService = Depends(get_reporting_service),
    _: User = Depends(get_current_user),
):
    return svc.inventory_health(scope=scope)


@router.get("/export.csv")
def export_report_csv(
    report: str = Query(
        ...,
        pattern="^(sales_trends|checkouts_by_genre|top_titles|inventory_health)$",
    ),
    days: int = Query(365, ge=1, le=3650),
    bucket: str = Query("month", pattern="^(week|month)$"),
    metric: str = Query("revenue", pattern="^(revenue|quantity)$"),
    limit: int = Query(10, ge=1, le=25),
    scope: str = Query("all", pattern="^(all|attention_only)$"),
    svc: ReportingService = Depends(get_reporting_service),
    _: User = Depends(get_current_user),
):
    filenames = {
        REPORT_SALES_TRENDS: "sales_trends.csv",
        REPORT_CHECKOUTS_BY_GENRE: "checkouts_by_genre.csv",
        REPORT_TOP_TITLES: "top_titles.csv",
        REPORT_INVENTORY_HEALTH: "inventory_health.csv",
    }
    return _csv_response(
        filenames[report],
        svc.export_csv(
            report=report,
            days=days,
            bucket=bucket,
            metric=metric,
            limit=limit,
            scope=scope,
        ),
    )
