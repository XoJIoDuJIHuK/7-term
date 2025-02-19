from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.consumers.translator.schemes import TranslationMessage
from src.database.repos.article import ArticleRepo
from src.database.repos.language import LanguageRepo
from src.database.repos.model import ModelRepo
from src.database.repos.prompt import PromptRepo
from src.database.repos.translation_task import TaskRepo
from src.depends import get_session
from src.http_responses import get_responses
from src.responses import BaseResponse
from src.routers.translation.schemes import (
    CreateTaskScheme,
    CreateTranslationScheme,
)
from src.settings import RabbitMQConfig, Role
from src.util.auth.classes import JWTCookie
from src.util.auth.schemes import UserInfo
from src.util.brokers.producer.rabbitmq import publish_message

router = APIRouter(prefix='/translation', tags=['Translation'])


@router.post(
    '/',
    response_model=BaseResponse,
    responses=get_responses(400, 401, 403, 404),
)
async def create_translation(
    translation_data: CreateTranslationScheme,
    db_session: AsyncSession = Depends(get_session),
    user_info: UserInfo = Depends(JWTCookie(roles=[Role.user])),
):
    # TODO: make source_language_id nullable
    article = await ArticleRepo.get_by_id(
        article_id=translation_data.article_id, db_session=db_session
    )
    if not article or article.user_id != user_info.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Статья не найдена'
        )
    if article.original_article_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нельзя переводить перевод',
        )
    if not await ModelRepo.exists_by_id(
        model_id=translation_data.model_id, db_session=db_session
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Модель не существует',
        )
    if not await PromptRepo.exists_by_id(
        prompt_id=translation_data.prompt_id, db_session=db_session
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Промпт не существует',
        )

    # producer = KafkaProducer(
    #     bootstrap_servers=KafkaConfig.address,
    #     topic=KafkaConfig.translation_topic,
    # )

    for target_language_id in translation_data.target_language_ids:
        if not await LanguageRepo.exists(
            language_id=target_language_id, db_session=db_session
        ):
            # TODO: change logic so not all translations cancel
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Конечный язык не поддерживается',
            )
        task = await TaskRepo.create(
            task_data=CreateTaskScheme(
                article_id=translation_data.article_id,
                model_id=translation_data.model_id,
                prompt_id=translation_data.prompt_id,
                target_language_id=target_language_id,
            ),
            db_session=db_session,
        )
        message = TranslationMessage(task_id=task.id)
        # message.retry_count += 1  # what does it do?
        # await producer.send_message(message.model_dump(mode='json'))

        rabbitmq_config = RabbitMQConfig()
        publish_message(
            rabbitmq_config.translation_topic, message.model_dump(mode='json')
        )
        return BaseResponse(message='Перевод запущен. Ожидайте')
