from fastapi import APIRouter

from app.api.schemas.info import InfoResponse
from app.core.config import settings

router = APIRouter()


@router.get("", response_model=InfoResponse)
async def app_info() -> InfoResponse:
    return InfoResponse(
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
    )
