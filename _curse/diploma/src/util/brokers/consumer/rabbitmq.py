import asyncio
import json
from abc import ABC
from dataclasses import dataclass

from pika import BlockingConnection, ConnectionParameters, credentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.consumers.translator.schemes import TranslationMessage
from src.database import get_session
from src.database.models import (
    AIModel,
    Article,
    Language,
    NotificationType,
    StylePrompt,
    TranslationTask,
    TranslationTaskStatus,
)
from src.database.repos.article import ArticleRepo
from src.database.repos.language import LanguageRepo
from src.database.repos.model import ModelRepo
from src.database.repos.prompt import PromptRepo
from src.database.repos.translation_task import TaskRepo
from src.logger import get_logger
from src.routers.articles.schemes import CreateArticleScheme
from src.routers.notifications.schemes import NotificationCreateScheme
from src.settings import RabbitMQConfig, NotificationConfig
from src.util.notifications.helpers import send_notification
from src.util.translator.classes import Gpt4freeTranslator

logger = get_logger(__name__)
rabbit_config = RabbitMQConfig()
notification_config = NotificationConfig()


@dataclass
class TranslationData:
    task: TranslationTask
    source_article: Article
    source_language: Language | None
    target_language: Language
    prompt: StylePrompt
    model: AIModel


class AbstractConsumer(ABC):
    def run(self, queue_name: str):
        connection = BlockingConnection(
            ConnectionParameters(
                rabbit_config.host,
                credentials=credentials.PlainCredentials(
                    rabbit_config.login, rabbit_config.password
                ),
            )
        )
        channel = connection.channel()
        channel.queue_declare(queue_name)

        channel.basic_consume(
            queue=queue_name,
            auto_ack=True,
            on_message_callback=self.__on_message,
        )

        channel.start_consuming()

    async def __on_message(self, ch, method, properties, body):
        pass


class TranslationConsumer(AbstractConsumer):
    translator = Gpt4freeTranslator()

    @staticmethod
    def __error_includes(substrings: list[str], error_data: dict):
        return any(
            [substr in error_data['error']['message'] for substr in substrings]
        )

    @staticmethod
    async def __check_message_consistency(
        message: TranslationMessage, db_session: AsyncSession
    ) -> TranslationData:
        task = await TaskRepo.get_by_id(
            task_id=message.task_id, db_session=db_session
        )
        if not task:
            raise Exception(
                f'Задача с идентификатором {message.task_id} не найдена'
            )
        article = await ArticleRepo.get_by_id(
            article_id=task.article_id, db_session=db_session
        )
        if not article:
            raise Exception(
                f'Исходная статья не найдена по'
                f' идентификатору: {task.article_id}'
            )
        source_lang = await LanguageRepo.get_by_id(
            language_id=article.language_id, db_session=db_session
        )
        target_lang = await LanguageRepo.get_by_id(
            language_id=task.target_language_id, db_session=db_session
        )
        if not target_lang:
            raise Exception(
                f'Конечный язык не найден по идентификатору:'
                f' {task.target_language_id}'
            )
        model = await ModelRepo.get_by_id(
            model_id=task.model_id, db_session=db_session
        )
        if not model:
            raise Exception(
                f'Модель не найдена по идентификатору: {task.model_id}'
            )
        prompt_object = await PromptRepo.get_by_id(
            prompt_id=task.prompt_id, db_session=db_session
        )
        if not prompt_object:
            raise Exception(
                f'Промпт не найден по идентификатору: {task.prompt_id}'
            )

        task.status = TranslationTaskStatus.started
        # db_session.add(task)
        await db_session.flush()

        return TranslationData(
            task=task,
            source_article=article,
            source_language=source_lang,
            target_language=target_lang,
            prompt=prompt_object,
            model=model,
        )

    @classmethod
    def __get_error_message(
        cls, task_data: TranslationData | None, e: Exception
    ) -> dict | None:
        if not task_data:
            logger.error('Uninevitable happened: task_data is None')
            return
        if not task_data.task.data:
            task_data.task.data = {}
        task_data.task.status = TranslationTaskStatus.failed
        error_data = json.loads(str(e))
        error_message = str(e)
        if 'error' in error_data:
            if 'message' in error_data['error']:
                logger.warning(
                    f'ERROR MESSAGE: {error_data["error"]["message"]}'
                )
                if cls.__error_includes(
                    substrings=['ProviderNotFound'],
                    error_data=error_data,
                ):
                    error_message = (
                        f'Модель {task_data.model.show_name} недоступна.'
                        f' Попробуйте другую'
                    )
                elif cls.__error_includes(
                    substrings=['ERR_BN_LIMIT', 'RateLimit'],
                    error_data=error_data,
                ):
                    error_message = (
                        f'Модель {task_data.model.show_name} временно '
                        f'недоступна. Попробуйте позже'
                    )
                else:
                    error_message = error_data['error']['message']
            else:
                logger.warning(
                    f'Unable to retrieve message from error: {error_data}'
                )
        else:
            logger.warning(
                f'Unable to retrieve error data from exception: {error_data}'
            )
        return {'error': error_message}

    def __on_message(self, ch, method, properties, body):
        asyncio.run(self.__process_message(ch, method, properties, body))

    async def __process_message(self, ch, method, properties, body):
        task_data = None
        async with get_session() as db_session:
            try:
                logger.info('ch: %s', ch)
                logger.info('method: %s', method)
                logger.info('properties: %s', properties)
                logger.info('body type: %s, value: %s', type(body), body)
                logger.info('Parsed body: %s', type(json.loads(body)))
                message = TranslationMessage.model_validate(json.loads(body))
                logger.info('Task ID: %s', message.task_id)

                error_message = None

                task_data = await self.__check_message_consistency(
                    message, db_session
                )
                translated_title = await self.translator.translate(
                    text=task_data.source_article.title,
                    target_language=task_data.target_language,
                    source_language=task_data.source_language,
                    model=task_data.model,
                    prompt_object=task_data.prompt,
                )
                logger.info(f'Translated title: {translated_title}')

                translated_text = await self.translator.translate(
                    text=task_data.source_article.text,
                    target_language=task_data.target_language,
                    source_language=task_data.source_language,
                    model=task_data.model,
                    prompt_object=task_data.prompt,
                )
                logger.info(f'Translated text: {translated_text}')

                translated_article = await ArticleRepo.create(
                    article_data=CreateArticleScheme(
                        title=translated_title,
                        text=translated_text,
                        user_id=task_data.source_article.user_id,
                        language_id=task_data.target_language.id,
                        original_article_id=task_data.source_article.id,
                    ),
                    db_session=db_session,
                )
                db_session.add(translated_article)
                await db_session.flush()
                await db_session.refresh(translated_article)
                await db_session.refresh(task_data.source_article)

                task_data.task.status = TranslationTaskStatus.completed
                task_data.task.translated_article_id = translated_article.id

            except Exception as e:
                logger.exception(e)
                error_message = self.__get_error_message(task_data, e)
                assert task_data is not None  # TODO: do something with this
                task_data.task.data = error_message

            # db_session.add(task_data.task)
            await db_session.commit()
            await db_session.refresh(task_data.task)
            await db_session.refresh(task_data.target_language)
            await db_session.refresh(task_data.source_article)

            translation_error = bool(task_data.task.data)
            await send_notification(
                notification_scheme=NotificationCreateScheme(
                    title=(
                        notification_config.Subjects.translation_ended
                        if not translation_error
                        else notification_config.Subjects.translation_error
                    ),
                    text=(
                        notification_config.translation_success_message.format(
                            article_name=task_data.source_article.title,
                            target_lang=task_data.target_language.name,
                        )
                        if not translation_error
                        else str(task_data.task.data)
                    ),
                    type=(
                        NotificationType.info
                        if not translation_error
                        else NotificationType.error
                    ),
                    user_id=task_data.source_article.user_id,
                ),
                db_session=db_session,
            )
            logger.info('Gracefully returning')
