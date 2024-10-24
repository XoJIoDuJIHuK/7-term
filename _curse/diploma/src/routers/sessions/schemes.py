import uuid
from datetime import datetime

from src.responses import Scheme


class SessionOutScheme(Scheme):
    id: uuid.UUID
    user_id: uuid.UUID
    ip: str
    is_closed: bool
    refresh_token_id: uuid.UUID
    created_at: datetime
    closed_at: datetime | None
