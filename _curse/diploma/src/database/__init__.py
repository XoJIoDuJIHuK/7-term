from src.settings import Database

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


engine = create_async_engine(
    Database.url,
    pool_size=Database.pool_size,
    max_overflow=Database.max_overflow,
    pool_recycle=Database.pool_recycle,
    pool_pre_ping=Database.pool_pre_ping
)
Session = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session