"""
Base pattern for standalone scripts that need DB/app context outside of FastAPI.

Run with: uv run python -m scripts.seed_db
"""

import asyncio

from app.core.db import AsyncSessionLocal
from app.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


async def main() -> None:
    setup_logging()
    logger.info("Seeding database...")

    async with AsyncSessionLocal() as _db:
        # Example: add rows, then commit.
        #   _db.add(MyModel(...))
        #   await _db.commit()
        pass

    logger.info("Done.")


if __name__ == "__main__":
    asyncio.run(main())
