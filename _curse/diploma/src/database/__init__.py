import asyncio
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator

from fastapi import HTTPException

from src.settings import Database, LOGGER_PREFIX
from src.logger import get_logger

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker

database_config = Database()
async_engine = create_async_engine(
    database_config.url,
)
AsyncDBSession = async_sessionmaker(async_engine)

engine = create_engine(database_config.url)
SyncDBSession = sessionmaker(engine)

logger = get_logger(LOGGER_PREFIX + __name__)
semaphore = asyncio.Semaphore(5)


class Base(DeclarativeBase):
    pass


@contextmanager
def get_synchronous_session():
    session = SyncDBSession()
    try:
        yield session
    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        logger.warning('Session rollback because of exception: %s', e)
        session.rollback()
        raise e
    finally:
        session.close()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with semaphore:
        async with AsyncDBSession() as session:
            try:
                yield session
            except HTTPException as e:
                await session.rollback()
                raise e
            except Exception as e:
                logger.warning('Session rollback because of exception: %s', e)
                await session.rollback()
                raise e
            finally:
                await session.close()
