import logging

from fastapi import WebSocket

from src.routers.notifications.schemes import NotificationOutScheme
from src.util.storage.classes import RedisHandler

logger = logging.getLogger(__name__)


async def push_notifications(
        websocket: WebSocket
):
    pubsub = RedisHandler().get_pubsub()
    # await pubsub.subscribe(
    #     NotificationConfig.topic_name.format(user_info.id)
    # )
    await websocket.send_json('xd 0')
    await websocket.send_json('xd 1')
    pubsub.subscribe('notifications')
    await websocket.send_json('xd 2')
    for message in pubsub.listen():
        print('MESSAGE', message)
        await websocket.send_json(message)
        if message['type'] == 'message':
            notification_data = message['data'].decode('utf-8')
            try:
                notification = NotificationOutScheme.model_validate_json(
                    notification_data
                )
                await websocket.send_json(
                    notification.model_dump(exclude_unset=True)
                )
            except Exception as e:
                logger.exception(
                    f'Invalid notification data: {notification_data},'
                    f' error: {e}'
                )