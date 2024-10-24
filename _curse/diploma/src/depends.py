from typing import AsyncGenerator

from src.database import get_session as get_db_session

from sqlalchemy.ext.asyncio import AsyncSession


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db_session() as session:
        yield session
