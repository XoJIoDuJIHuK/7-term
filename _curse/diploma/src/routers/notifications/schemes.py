import uuid
from datetime import datetime

from src.database.models import NotificationType
from src.responses import Scheme


class NotificationBase(Scheme):
    title: str
    text: str
    type: NotificationType
    created_at: datetime


class CreateNotificationScheme(NotificationBase):
    user_id: uuid.UUID


class NotificationOutScheme(NotificationBase):
    id: uuid.UUID
    read_at: datetime
