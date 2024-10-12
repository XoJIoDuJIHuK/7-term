import uuid
from datetime import datetime

from pydantic import BaseModel


class UploadArticleScheme(BaseModel):
    title: str
    text: str

    class Config:
        from_attributes = True


class EditArticleScheme(UploadArticleScheme):
    title: str | None
    text: str | None


class CreateArticleScheme(UploadArticleScheme):
    user_id: uuid.UUID
    language_id: uuid.UUID | None
    original_article_id: uuid.UUID | None
    like: bool | None


class ArticleOutScheme(CreateArticleScheme):
    id: uuid.UUID
    created_at: datetime
    deleted_at: datetime | None