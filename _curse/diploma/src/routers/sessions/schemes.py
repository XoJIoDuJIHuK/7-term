import uuid
from datetime import datetime

from pydantic import BaseModel


class SessionOutScheme(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    ip: str
    is_active: bool
    is_closed: bool
    refresh_token_id: uuid.UUID
    created_at: datetime
    closed_at: datetime | None

    class Config:
        from_attributes = True
