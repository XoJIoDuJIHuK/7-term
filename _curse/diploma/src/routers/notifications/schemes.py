import uuid
from datetime import datetime

from src.database.models import NotificationType
from src.responses import Scheme


class NotificationBase(Scheme):
    title: str
    text: str
    type: NotificationType


class NotificationCreateScheme(NotificationBase):
    user_id: uuid.UUID


class NotificationOutScheme(NotificationBase):
    id: uuid.UUID
    created_at: datetime
    read_at: datetime | None
