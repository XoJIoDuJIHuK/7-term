import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Notification
from src.routers.notifications.schemes import NotificationOutScheme
from src.util.time.helpers import get_utc_now


class NotificationRepository:
    @staticmethod
    async def get_notifications(
            user_id: uuid.UUID,
            db_session: AsyncSession
    ) -> list[NotificationOutScheme]:
        result = await db_session.execute(select(Notification).where(
            Notification.user_id == user_id,
            Notification.read_at.is_(None)
        ))
        notifications = result.scalars().all()
        return [
            NotificationOutScheme.model_validate(n) for n in notifications
        ]

    @staticmethod
    async def read_all(
            user_id: uuid.UUID,
            max_datetime: datetime,
            db_session: AsyncSession
    ) -> int:
        result = await db_session.execute(update(Notification).where(
            Notification.user_id == user_id,
            Notification.created_at <= max_datetime
        ).values(read_at=get_utc_now()))
        return result.rowcount
