from datetime import datetime

from pydantic import Field

from src.responses import Scheme


class CreatePromptScheme(Scheme):
    title: str = Field(min_length=1, max_length=20)
    text: str = Field(min_length=1)


class EditPromptScheme(CreatePromptScheme):
    title: str | None = Field(None, min_length=1, max_length=20)
    text: str | None = Field(None, min_length=1)


class PromptOutScheme(Scheme):
    id: int
    title: str


class PromptOutAdminScheme(PromptOutScheme):
    text: str
    created_at: datetime
