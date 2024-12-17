from datetime import datetime

from pydantic import Field

from src.responses import Scheme


class ModelCreateScheme(Scheme):
    show_name: str = Field(min_length=0, max_length=50)
    name: str = Field(min_length=0)
    provider: str = Field(min_length=0)


class ModelUpdateScheme(Scheme):
    show_name: str | None = Field(min_length=0, max_length=50)
    name: str | None = Field(min_length=0)
    provider: str | None = Field(min_length=0)


class ModelOutScheme(Scheme):
    show_name: str
    id: int


class ModelAdminOutScheme(ModelCreateScheme):
    id: int
    created_at: datetime
