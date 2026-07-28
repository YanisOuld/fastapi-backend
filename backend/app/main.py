import argparse
from contextlib import asynccontextmanager

import uvicorn
from backend.app.api.router import api_router
from backend.app.core.config import settings
from backend.app.core.db import engine
from backend.app.core.exceptions import register_exception_handlers
from backend.app.core.logging import get_logger, setup_logging
from backend.app.core.redis import close_redis
from backend.app.middlewares.cors import add_cors_middleware
from backend.app.middlewares.logging import LoggingMiddleware
from backend.app.middlewares.request_id import RequestIDMiddleware
from fastapi import FastAPI

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


def run() -> None:
    parser = argparse.ArgumentParser(description="Run the FastAPI application.")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    uvicorn.run(
        "backend.app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    run()
