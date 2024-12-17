import uuid
from datetime import datetime
from pydantic import Field

from src.database.models import Article
from src.responses import Scheme
from src.settings import TextTranslationConfig


class UploadArticleScheme(Scheme):
    title: str = Field(min_length=1, max_length=50)
    text: str = Field(
        min_length=1,
        max_length=TextTranslationConfig.max_text_length
    )
    language_id: int | None


class EditArticleScheme(Scheme):
    title: str | None = Field(None, min_length=1, max_length=50)
    text: str | None = Field(
        None,
        min_length=1,
        max_length=TextTranslationConfig.max_text_length
    )
    language_id: int | None = None


class ArticleUpdateLikeScheme(Scheme):
    like: bool | None


class CreateArticleScheme(UploadArticleScheme):
    title: str = Field(min_length=1)
    user_id: uuid.UUID
    language_id: int | None = None
    original_article_id: uuid.UUID | None = None
    like: bool | None = None


class ArticleOutScheme(CreateArticleScheme):
    id: uuid.UUID
    created_at: datetime
    deleted_at: datetime | None = None
    report_exists: bool = False

    @classmethod
    def create(cls, article_object: Article, report_exists: bool):
        scheme_object = cls.model_validate(article_object)
        scheme_object.report_exists = report_exists
        return scheme_object


class ArticleListItemScheme(Scheme):
    id: uuid.UUID
    title: str
    language_id: int | None = None
    like: bool | None = None
    created_at: datetime
