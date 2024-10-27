import json
import logging
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    WebSocket,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect

from src.depends import get_session
from src.routers.notifications.schemes import NotificationOutScheme
from src.services.notification import NotificationRepository
from src.settings import LOGGER_PREFIX, NotificationConfig
from src.util.auth.classes import JWTBearer
from src.util.auth.schemes import UserInfo
from src.util.storage.classes import RedisHandler

router = APIRouter(
    prefix='/notifications',
    tags=['Notifications']
)
logger = logging.getLogger(LOGGER_PREFIX + __name__)


@router.websocket(
    '/'
)
async def get_notifications(
        websocket: WebSocket,
        user_info: UserInfo = Depends(JWTBearer()),
        db_session: AsyncSession = Depends(get_session)
):
    await websocket.accept()
    pubsub = RedisHandler().get_pubsub()
    try:
        await pubsub.subscribe(
            NotificationConfig.topic_name.format(user_info.id)
        )
        notifications = await NotificationRepository.get_notifications(
            user_id=user_info.id,
            db_session=db_session
        )
        await websocket.send_json(json.dumps([
            n.model_dump_json() for n in notifications
        ]))
        async for message in pubsub.listen():
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

    except WebSocketDisconnect:
        logger.exception(f'WebSocket connection closed for user {user_info}')
        pubsub.unsubscribe(NotificationConfig.topic_name.format(user_info.id))
    except Exception:
        pubsub.unsubscribe(NotificationConfig.topic_name.format(user_info.id))
        await websocket.close()
