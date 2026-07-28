from backend.app.api.schemas.info import InfoResponse
from backend.app.core.config import settings
from fastapi import APIRouter

router = APIRouter()


@router.get("", response_model=InfoResponse)
async def app_info() -> InfoResponse:
    return InfoResponse(
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
    )
