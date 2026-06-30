from app.schemas.base import AppSchema


class InfoResponse(AppSchema):
    name: str
    version: str
    debug: bool
