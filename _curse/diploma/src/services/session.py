import uuid
from typing import List, Tuple

from src.database.models import Session

from sqlalchemy import Sequence, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.pagination import PaginationParams, paginate
from src.routers.sessions.schemes import SessionOutScheme


class SessionRepository:
    @staticmethod
    async def get_refresh_token_ids(
            user_id: uuid.UUID,
            db_session: AsyncSession
    ) -> list[uuid.UUID]:
        result = await db_session.execute(select(
            Session.refresh_token_id
        ).filter_by(user_id=user_id))
        return list(result.scalars().all())

    @staticmethod
    async def get_list(
            user_id: uuid.UUID,
            pagination_params: PaginationParams,
            db_session: AsyncSession
    ) -> Tuple[List[SessionOutScheme], int]:
        query = select(Session).where(
            Session.user_id == user_id,
            Session.is_closed.is_(False)
        )
        sessions, count = await paginate(
            session=db_session,
            statement=query,
            pagination=pagination_params
        )
        sessions_list = [
            SessionOutScheme.model_validate(a) for a in sessions
        ]
        return sessions_list, count

    @staticmethod
    async def get_by_refresh_id(
            refresh_token_id: uuid.UUID,
            db_session: AsyncSession
    ) -> Session | None:
        result = await db_session.execute(select(Session).filter_by(
            refresh_token_id=refresh_token_id
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def close_all(
            user_id: uuid.UUID,
            db_session: AsyncSession
    ):
        result = await db_session.execute(update(Session).where(
            Session.user_id == user_id
        ).values(is_closed=True))
        await db_session.commit()
        return result.rowcount

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
