import asyncio
import json
import logging

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
)

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect

from src.depends import get_session, validate_token_for_ws
from src.responses import BaseResponse
from src.routers.notifications.schemes import NotificationOutScheme
from src.database.repos.notification import NotificationRepo
from src.settings import LOGGER_PREFIX, NotificationConfig
from src.util.auth.classes import JWTCookie
from src.util.auth.schemes import UserInfo
from src.util.storage.classes import RedisHandler
from src.util.time.helpers import get_utc_now

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
        user_info: UserInfo = Depends(validate_token_for_ws),
        db_session: AsyncSession = Depends(get_session)
):
    try:
        await websocket.accept()

        notifications = await NotificationRepo.get_list(
            user_id=user_info.id,
            db_session=db_session
        )
        await websocket.send_json(
            json.dumps([n.model_dump_json() for n in notifications])
        )

        pubsub = RedisHandler().get_pubsub()
        await pubsub.subscribe(
            NotificationConfig.topic_name.format(user_info.id)
        )
        while True:
            try:
                message = await pubsub.get_message(timeout=0.5)
                if message and message['type'] == 'message':
                    notification_data = message['data'].decode('utf-8')
                    try:
                        notification = NotificationOutScheme.model_validate_json(
                            notification_data
                        )
                        await websocket.send_json(
                            notification.model_dump(exclude_unset=True)
                        )
                    except Exception as e:
                        logger.exception(e)
                await asyncio.sleep(0)

            except Exception as e:
                logger.exception(e)
                break

    except WebSocketDisconnect:
        logger.error(f'WebSocket connection closed')
    except Exception as e:
        logger.exception(e)
        await websocket.close()


@router.put(
    '/',
    response_model=BaseResponse
)
async def mark_notifications_read(
        user_info: UserInfo = Depends(JWTCookie()),
        db_session: AsyncSession = Depends(get_session)
):
    closed_notifications = await NotificationRepo.read_all(
        user_id=user_info.id,
        max_datetime=get_utc_now(),
        db_session=db_session
    )
    return BaseResponse(message=f'Cleared {closed_notifications}'
                                f' notifications')
