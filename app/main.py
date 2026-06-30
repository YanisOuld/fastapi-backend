from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.db import engine
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.redis import close_redis
from app.middlewares.cors import add_cors_middleware
from app.middlewares.logging import LoggingMiddleware
from app.middlewares.request_id import RequestIDMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    setup_logging(debug=settings.DEBUG)
    logger.info("Starting %s v%s", settings.PROJECT_NAME, settings.VERSION)
    yield
    logger.info("Shutting down...")
    await engine.dispose()
    await close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

register_exception_handlers(app)
add_cors_middleware(app)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)
