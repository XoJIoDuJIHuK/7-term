from fastapi import (
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repos.notification import NotificationRepo
from src.routers.notifications.schemes import NotificationCreateScheme, \
    NotificationOutScheme
from src.settings import NotificationConfig
from src.util.storage.classes import RedisHandler


async def send_notification(
        notification_scheme: NotificationCreateScheme,
        db_session: AsyncSession,
) -> None:
    notification = (
        await NotificationRepo.create(notification_scheme, db_session)
    )
    redis_client = RedisHandler().client
    redis_client.publish(
        NotificationConfig.topic_name.format(notification_scheme.user_id),
        message=(
            NotificationOutScheme
            .model_validate(notification)
            .model_dump_json()
        )
    )
