import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_info_returns_app_metadata(client: AsyncClient):
    response = await client.get("/api/v1/info")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == settings.PROJECT_NAME
    assert body["version"] == settings.VERSION
    assert "debug" in body
