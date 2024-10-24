import uuid
from datetime import datetime

from src.responses import Scheme


class UploadArticleScheme(Scheme):
    title: str
    text: str


class EditArticleScheme(Scheme):
    title: str | None = None
    text: str | None = None


class CreateArticleScheme(UploadArticleScheme):
    user_id: uuid.UUID
    language_id: int | None = None
    original_article_id: uuid.UUID | None = None
    like: bool | None = None


class ArticleOutScheme(CreateArticleScheme):
    id: uuid.UUID
    created_at: datetime
    deleted_at: datetime | None = None


class ArticleListItemScheme(Scheme):
    id: uuid.UUID
    title: str
    language_id: int | None = None
    like: bool | None = None
    created_at: datetime
