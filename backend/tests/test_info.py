import pytest
from backend.app.core.config import settings
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_info_returns_app_metadata(client: AsyncClient):
    response = await client.get("/api/v1/info")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == settings.PROJECT_NAME
    assert body["version"] == settings.VERSION
    assert "debug" in body
