import uuid

from pydantic import BaseModel, Field


class TranslationMessage(BaseModel):
    task_id: uuid.UUID = Field(
        examples=['c6e98bce-3335-49be-aa27-fe6631e7f0da']
    )
    retry_count: int = Field(
        default=0
    )
    resend_count: int = Field(
        default=0
    )
