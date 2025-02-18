from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repos.notification import NotificationRepo
from src.logger import get_logger
from src.routers.notifications.schemes import (
    NotificationCreateScheme,
    NotificationOutScheme,
)
from src.settings import NotificationConfig
from src.util.storage.classes import RedisHandler


logger = get_logger(__name__)
notification_config = NotificationConfig()


async def send_notification(
    notification_scheme: NotificationCreateScheme,
    db_session: AsyncSession,
) -> None:
    logger.warning(
        f'Sending notification {notification_scheme.title} '
        f'to {notification_scheme.user_id}'
    )
    notification = await NotificationRepo.create(
        notification_scheme, db_session
    )
    redis_client = RedisHandler().client
    await redis_client.publish(
        notification_config.topic_name.format(notification_scheme.user_id),
        message=(
            NotificationOutScheme.model_validate(
                notification
            ).model_dump_json()
        ),
    )
