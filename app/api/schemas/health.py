from typing import Literal

from app.schemas.base import AppSchema


class HealthChecks(AppSchema):
    database: Literal["ok", "unreachable"]
    redis: Literal["ok", "unreachable"]


class HealthResponse(AppSchema):
    status: Literal["ok", "degraded"]
    checks: HealthChecks
