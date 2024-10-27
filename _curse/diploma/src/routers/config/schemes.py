import uuid

from src.responses import Scheme


class CreateConfigScheme(Scheme):
    name: str
    prompt_id: int | None = None
    model_id: int | None = None
    language_ids: list[int]


class EditConfigScheme(CreateConfigScheme):
    pass


class ConfigOutScheme(CreateConfigScheme):
    id: int
    user_id: uuid.UUID
