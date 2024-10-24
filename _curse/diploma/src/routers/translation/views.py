import uuid

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.consumers.translator.schemes import TranslationMessage
from src.depends import get_session
from src.http_responses import get_responses
from src.responses import BaseResponse
from src.routers.translation.schemes import CreateTranslationScheme, \
    CreateTaskScheme
from src.services.article import ArticleRepository
from src.services.language import LanguageRepository
from src.services.model import ModelRepository
from src.services.prompt import PromptRepository
from src.services.translation_task import TaskRepository
from src.settings import KafkaConfig, Role
from src.util.auth.classes import JWTBearer
from src.util.auth.schemes import UserInfo
from src.util.brokers.producer.kafka import KafkaProducer

tokens = {
    'p-b': 's_VxVxW7YX9HOOnc7b5-lA%3D%3D',
    'p-lat': 'Il66gBgIY%2BGe302zVz71xCj6WWmSaHZ1ICwhsstzvg%3D%3D',
}

router = APIRouter(
    prefix='/translation',
    tags=['Translation']
)


@router.post(
    '/',
    response_model=BaseResponse,
    responses=get_responses(400, 401, 403, 404)
)
async def create_translation(
        translation_data: CreateTranslationScheme,
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.user]))
):
    # TODO: make source_language_id nullable
    article = await ArticleRepository.get_by_id(
        article_id=translation_data.article_id,
        db_session=db_session
    )
    if not article or article.user_id != user_info.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Статья не найдена'
        )
    if article.original_article_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя переводить перевод'
        )
    if (
        translation_data.source_language_id
        and not await LanguageRepository.exists(
            language_id=translation_data.source_language_id,
            db_session=db_session
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Исходный язык не поддерживается'
        )
    if not await ModelRepository.exists_by_id(
        model_id=translation_data.model_id,
        db_session=db_session
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Модель не существует'
        )
    if not await PromptRepository.exists_by_id(
        prompt_id=translation_data.prompt_id,
        db_session=db_session
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Промпт не существует'
        )

    producer = KafkaProducer(
        bootstrap_servers=KafkaConfig.address,
        topic=KafkaConfig.translation_topic
    )

    for target_language_id in translation_data.target_language_ids:
        if not await LanguageRepository.exists(
                language_id=target_language_id,
                db_session=db_session
        ):
            # TODO: change logic so not all translations cancel
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Конечный язык не поддерживается'
            )
        task = await TaskRepository.create(
            task_data=CreateTaskScheme(
                article_id=translation_data.article_id,
                model_id=translation_data.model_id,
                prompt_id=translation_data.prompt_id,
                source_language_id=translation_data.source_language_id,
                target_language_id=target_language_id
            ),
            db_session=db_session
        )
        message = TranslationMessage(task_id=task.id)
        # message.retry_count += 1  # what does it do?
        await producer.send_message(
            message.model_dump(mode='json')
        )
        return BaseResponse(message='Перевод запущен. Ожидайте')

