import uuid

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Path,
    status,
)

from fastapi_pagination import Params
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.routers.articles.schemes import (
    ArticleOutScheme,
    CreateArticleScheme,
    EditArticleScheme,
    UploadArticleScheme,
)
from src.services.article import ArticleRepository
from src.settings import Role
from src.util.auth.classes import JWTBearer
from src.util.auth.schemes import UserInfo
from src.util.time.helpers import get_utc_now

router = APIRouter(
    prefix='/articles',
    tags=['Articles']
)


@router.get(
    '/'
)
async def get_list(
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.user])),
        pagination_params: Params = Depends(),
        db_session: AsyncSession = Depends(get_session)
):
    page = await ArticleRepository.get_list(
        user_id=user_info.id,
        pagination_params=pagination_params,
        db_session=db_session
    )
    page.items = [ArticleOutScheme.model_validate(a) for a in page.items]


@router.post(
    '/'
)
async def upload_article(
        article_data: UploadArticleScheme,
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.user])),
        db_session: AsyncSession = Depends(get_session)
):
    article = await ArticleRepository.create(
        article_data=CreateArticleScheme(
            title=article_data.title,
            text=article_data.text,
            user_id=user_info.id
        ),
        db_session=db_session
    )
    return ArticleOutScheme.model_validate(article)


@router.put(
    '/{article_id}/'
)
async def update_article(
        new_article_data: EditArticleScheme,
        article_id: uuid.UUID = Path(),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.user])),
        db_session: AsyncSession = Depends(get_session),
):
    article = await ArticleRepository.get_by_id(article_id, db_session)
    if (
            not article
            or article.user_id != user_info.id
            or article.original_article_id is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Статья не найдена'
        )
    if new_article_data.title:
        article.title = new_article_data.title
    if new_article_data.text:
        article.title = new_article_data.text
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    return ArticleOutScheme.model_validate(article)


@router.delete(
    '/{article_id}/'
)
async def delete_article(
        article_id: uuid.UUID = Path(),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.user])),
        db_session: AsyncSession = Depends(get_session),
):
    article = await ArticleRepository.get_by_id(article_id, db_session)
    if not article or article.user_id != user_info.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Статья не найдена'
        )
    article.deleted_at = get_utc_now()
    db_session.add(article)
    await db_session.commit()
    await db_session.refresh(article)
    return ArticleOutScheme.model_validate(article)
