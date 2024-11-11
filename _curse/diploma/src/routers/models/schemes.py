from datetime import datetime

from pydantic import Field

from src.responses import Scheme


class CreateModelScheme(Scheme):
    name: str = Field(min_length=1, max_length=20)
    provider: str = Field(min_length=1, max_length=20)


class UpdateModelScheme(Scheme):
    name: str | None = Field(min_length=1, max_length=20)
    provider: str | None = Field(min_length=1, max_length=20)


class ModelOutScheme(CreateModelScheme):
    id: int


class ModelAdminOutScheme(ModelOutScheme):
    created_at: datetime
