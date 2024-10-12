import uuid

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from src.database.models import Article
from src.routers.articles.shemes import CreateArticleScheme

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ArticleRepository:
    @staticmethod
    async def get_list(
            user_id: uuid.UUID,
            pagination_params: Params,
            db_session: AsyncSession
    ) -> Page[Article]:
        # TODO: add filters and sorting
        query = select(Article).where(Article.user_id == user_id).where(
            Article.deleted_at.is_(None)
        )
        return await paginate(
            conn=db_session,
            query=query,
            params=pagination_params
        )

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
