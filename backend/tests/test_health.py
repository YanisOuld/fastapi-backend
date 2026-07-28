import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_ok(client: AsyncClient):
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["redis"] == "ok"


@pytest.mark.asyncio
async def test_health_degraded_when_db_down(client_db_down: AsyncClient):
    response = await client_db_down.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "unreachable"
    assert body["checks"]["redis"] == "ok"


@pytest.mark.asyncio
async def test_health_degraded_when_redis_down(client_redis_down: AsyncClient):
    response = await client_redis_down.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["redis"] == "unreachable"
