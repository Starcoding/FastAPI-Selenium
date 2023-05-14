from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from webdriver_manager.firefox import GeckoDriverManager
from app.config import settings


async def get_db() -> AsyncGenerator:
    db = AsyncSession(
        bind=create_async_engine(settings.get_db_uri, future=True, echo=False),
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    try:
        yield db
    finally:
        await db.close()


async def get_driver() -> str:
    path = GeckoDriverManager().install()
    return path
