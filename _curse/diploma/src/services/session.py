import uuid

from fastapi import HTTPException, status

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from src.database import get_session
from src.database.models import Session

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class SessionRepository:
    @staticmethod
    async def get_list(
            user_id: uuid.UUID,
            pagination_params: Params,
            db_session: AsyncSession
    ) -> Page[Session]:
        query = select(Session).where(
            Session.user_id == user_id
        )
        return await paginate(
            conn=db_session,
            query=query,
            params=pagination_params
        )

    @staticmethod
    async def close_all(
            user_id: uuid.UUID,
            db_session: AsyncSession
    ):
        result = await db_session.execute(update(Session).where(
            Session.user_id == user_id
        ).values(is_closed=True))
        return result

    @staticmethod
    async def create(
            user_id: uuid.UUID,
            refresh_token_id: uuid.UUID | None,
            ip: str,
            db_session: AsyncSession
    ) -> Session:
        session = Session(
            user_id=user_id,
            refresh_token_id=refresh_token_id,
            ip=ip
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        return session
