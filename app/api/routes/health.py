from fastapi import APIRouter, status
from sqlalchemy import text

from app.api.dependancies import DbSession, RedisClient
from app.api.schemas.health import HealthChecks, HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check(db: DbSession, redis: RedisClient) -> HealthResponse:
    db_status = "ok"
    redis_status = "ok"

    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unreachable"

    try:
        await redis.ping()
    except Exception:
        redis_status = "unreachable"

    checks = HealthChecks(database=db_status, redis=redis_status)
    return HealthResponse(
        status="ok" if db_status == "ok" and redis_status == "ok" else "degraded",
        checks=checks,
    )
