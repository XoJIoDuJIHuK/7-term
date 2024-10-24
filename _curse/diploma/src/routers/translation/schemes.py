import uuid

from src.responses import Scheme


class CreateTaskScheme(Scheme):
    article_id: uuid.UUID
    source_language_id: int | None
    target_language_id: int
    prompt_id: int
    model_id: int


class CreateTranslationScheme(Scheme):
    article_id: uuid.UUID
    source_language_id: int | None = None
    target_language_ids: list[int]
    prompt_id: int
    model_id: int
