from __future__ import annotations

from collections import deque
from time import perf_counter

from fastapi import APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

router = APIRouter(tags=["metrics"])

# Simple in-memory metrics (resets on restart)
_requests_total = 0
_errors_total = 0
_latencies_ms = deque(maxlen=5000)


def _p95(values: list[float]) -> float | None:
    if not values:
        return None
    values_sorted = sorted(values)
    idx = int(0.95 * (len(values_sorted) - 1))
    return values_sorted[idx]


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        global _requests_total, _errors_total

        start = perf_counter()
        status_code = 500

        try:
            response: Response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            elapsed_ms = (perf_counter() - start) * 1000.0
            _requests_total += 1
            _latencies_ms.append(elapsed_ms)

            if status_code >= 400:
                _errors_total += 1


@router.get("/metrics")
def metrics():
    lat_list = list(_latencies_ms)
    p95 = _p95(lat_list)
    error_rate = (_errors_total / _requests_total) if _requests_total else 0.0

    return {
        "requests_total": _requests_total,
        "errors_total": _errors_total,
        "error_rate": round(error_rate, 4),
        "latency_ms_p95": None if p95 is None else round(p95, 2),
        "window_size": len(lat_list),
    }
