import uuid

from pydantic import Field

from src.responses import Scheme


class CreateConfigScheme(Scheme):
    name: str = Field(min_length=1, max_length=20)
    prompt_id: int | None = None
    model_id: int | None = None
    language_ids: list[int]


class EditConfigScheme(CreateConfigScheme):
    pass


class ConfigOutScheme(CreateConfigScheme):
    id: int
    user_id: uuid.UUID
