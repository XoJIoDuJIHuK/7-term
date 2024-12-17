import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Notification
from src.routers.notifications.schemes import NotificationOutScheme, \
    NotificationCreateScheme
from src.util.time.helpers import get_utc_now


class NotificationRepo:
    @staticmethod
    async def get_list(
            user_id: uuid.UUID,
            db_session: AsyncSession
    ) -> list[NotificationOutScheme]:
        result = await db_session.execute(select(Notification).where(
            Notification.user_id == user_id,
            Notification.read_at.is_(None)
        ).order_by(Notification.created_at))
        notifications = result.scalars().all()
        return [
            NotificationOutScheme.model_validate(n) for n in notifications
        ]

    @staticmethod
    async def create(
            notification_scheme: NotificationCreateScheme,
            db_session: AsyncSession,
    ) -> Notification:
        notification_object = Notification(
            title=notification_scheme.title,
            text=notification_scheme.text,
            user_id=notification_scheme.user_id,
            type=notification_scheme.type
        )
        db_session.add(notification_object)
        await db_session.commit()
        await db_session.refresh(notification_object)
        return notification_object

    @staticmethod
    async def read_all(
            user_id: uuid.UUID,
            max_datetime: datetime,
            db_session: AsyncSession
    ) -> int:
        result = await db_session.execute(update(Notification).where(
            Notification.user_id == user_id,
            Notification.created_at <= max_datetime,
            Notification.read_at.is_(None)
        ).values(read_at=get_utc_now()))
        await db_session.commit()
        return result.rowcount
