import uuid

from src.responses import Scheme


class CreateConfigScheme(Scheme):
    name: str
    prompt_id: uuid.UUID | None
    model_id: int | None
    language_ids: list[int]


class EditConfigScheme(CreateConfigScheme):
    pass


class ConfigOutScheme(CreateConfigScheme):
    id: int
    user_id: uuid.UUID
