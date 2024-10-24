import uuid
from typing import List, Tuple

from fastapi_pagination import Page, Params
# from fastapi_pagination.ext.sqlalchemy import paginate

from src.database.models import Article
from src.pagination import PaginationParams, paginate
from src.routers.articles.schemes import ArticleOutScheme, CreateArticleScheme, \
    ArticleListItemScheme

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.util.time.helpers import get_utc_now


class ArticleRepository:
    @staticmethod
    async def get_list(
            user_id: uuid.UUID,
            pagination_params: PaginationParams,
            db_session: AsyncSession,
            original_article_id: uuid.UUID | None = None,
    ) -> Tuple[List[ArticleListItemScheme], int]:
        # TODO: add filters and sorting
        query = select(Article).where(
            Article.user_id == user_id,
            Article.deleted_at.is_(None)
        )
        if original_article_id is None:
            query = query.where(Article.original_article_id.is_(None))
        else:
            query = query.where(
                Article.original_article_id == original_article_id
            )
        articles, count = await paginate(
            session=db_session,
            statement=query,
            pagination=pagination_params
        )
        articles_list =[
            ArticleListItemScheme.model_validate(a) for a in articles
        ]
        return articles_list, count

    @staticmethod
    async def get_translations(
            original_article_id: uuid.UUID,
            db_session: AsyncSession
    ) -> list[ArticleListItemScheme]:
        result = await db_session.execute(select(Article).where(
            Article.deleted_at.is_(None),
            Article.original_article_id == original_article_id
        ))
        articles = result.scalars().all()
        return [
            ArticleListItemScheme.model_validate(a) for a in articles
        ]

    @staticmethod
    async def exists(
            article_id: uuid.UUID,
            db_session: AsyncSession,
            user_id: uuid.UUID | None = None,
    ) -> bool:
        query = select(exists().where(Article.id == article_id))
        if user_id is not None:
            query = query.where(Article.user_id == user_id)
        result = await db_session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(
            article_id: uuid.UUID,
            db_session: AsyncSession
    ) -> Article | None:
        result = await db_session.execute(select(Article).where(
            Article.id == article_id
        ))
        return result.scalars().first()

    @staticmethod
    async def create(
            article_data: CreateArticleScheme,
            db_session: AsyncSession
    ) -> Article:
        article = Article(
            title=article_data.title,
            text=article_data.text,
            user_id=article_data.user_id,
            language_id=article_data.language_id,
            original_article_id=article_data.original_article_id,
            like=article_data.like,
        )
        db_session.add(article)
        await db_session.commit()
        await db_session.refresh(article)
        return article

    @staticmethod
    async def update(
            article: Article,
            new_title: str | None,
            new_text: str | None,
            db_session: AsyncSession
    ) -> Article:

        db_session.add(article)
        await db_session.commit()
        await db_session.refresh(article)
        return article

    @staticmethod
    async def delete(
            article: Article,
            db_session: AsyncSession
    ) -> Article:
        article.deleted_at = get_utc_now()
        db_session.add(article)
        await db_session.commit()
        await db_session.refresh(article)
        return article
