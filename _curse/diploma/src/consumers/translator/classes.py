import asyncio
import json

from src.consumers.translator.schemes import TranslationMessage
from src.database import get_session
from src.database.models import TranslationTaskStatus, NotificationType
from src.database.repos.article import ArticleRepo
from src.database.repos.language import LanguageRepo
from src.database.repos.model import ModelRepo
from src.database.repos.prompt import PromptRepo
from src.database.repos.translation_task import TaskRepo
from src.logger import get_logger
from src.routers.articles.schemes import CreateArticleScheme
from src.routers.notifications.schemes import NotificationCreateScheme
from src.settings import (
    KafkaConfig,
    LOGGER_PREFIX,
    NotificationConfig,
    TranslationTaskConfig,
)
from src.util.brokers.consumer.kafka import AbstractKafkaConsumer
from src.util.brokers.producer.kafka import KafkaProducer
from src.util.notifications.helpers import send_notification
from src.util.translator.classes import Gpt4freeTranslator
from src.util.translator.exceptions import TranslatorAPITimeoutError


class TranslationTaskConsumer(AbstractKafkaConsumer):
    """Class that contains logic for handling Kafka consumer messages.

    Attributes:
        logger (logging.Logger): Logger instance for this class.
    """

    logger = get_logger(LOGGER_PREFIX + __name__)
    translator = Gpt4freeTranslator()

    async def on_message(self, msg):
        await asyncio.create_task(self.process_message(msg))


    def __error_includes(self, substrings: list[str], error_data: dict):
        return any([
            substr in error_data['error']['message'] for substr in substrings
        ])

    async def process_message(self, msg):
        message = TranslationMessage(**msg.value)
        error_message = None

        async with (get_session() as db_session):
            task = await TaskRepo.get_by_id(
                task_id=message.task_id,
                db_session=db_session
            )
            if not task:
                raise Exception(f'Задача с идентификатором'
                                f' {message.task_id} не найдена')

            try:
                article = await ArticleRepo.get_by_id(
                    article_id=task.article_id,
                    db_session=db_session
                )
                if not article:
                    raise Exception(f'Исходная статья не найдена по'
                                    f' идентификатору: {task.article_id}')
                source_lang = await LanguageRepo.get_by_id(
                    language_id=article.language_id,
                    db_session=db_session
                )
                target_lang = await LanguageRepo.get_by_id(
                    language_id=task.target_language_id,
                    db_session=db_session
                )
                if not target_lang:
                    raise Exception(
                        f'Конечный язык не найден по идентификатору:'
                        f' {task.target_language_id}'
                    )
                model = await ModelRepo.get_by_id(
                    model_id=task.model_id,
                    db_session=db_session
                )
                if not model:
                    raise Exception(f'Модель не найдена по идентификатору:'
                                    f' {task.model_id}')
                prompt_object = await PromptRepo.get_by_id(
                    prompt_id=task.prompt_id,
                    db_session=db_session
                )
                if not prompt_object:
                    raise Exception(f'Промпт не найден по идентификатору: '
                                    f'{task.prompt_id}')

                task.status = TranslationTaskStatus.started
                db_session.add(task)
                await db_session.flush()

                translated_title = await self.translator.translate(
                    text=article.title,
                    target_language=target_lang,
                    source_language=source_lang if source_lang else None,
                    model=model,
                    prompt_object=prompt_object
                )
                # self.logger.info(f'Translated title: {translated_title}')

                translated_text = await self.translator.translate(
                    text=article.text,
                    target_language=target_lang,
                    source_language=source_lang if source_lang else None,
                    model=model,
                    prompt_object=prompt_object
                )
                # self.logger.info(f'Translated text: {translated_text}')

                translated_article = await ArticleRepo.create(
                    article_data=CreateArticleScheme(
                        title=translated_title,
                        text=translated_text,
                        user_id=article.user_id,
                        language_id=target_lang.id,
                        original_article_id=article.id
                    ),
                    db_session=db_session
                )
                db_session.add(translated_article)
                await db_session.flush()
                await db_session.refresh(translated_article)
                await db_session.refresh(article)

                task.status = TranslationTaskStatus.completed
                task.translated_article_id = translated_article.id
            except TranslatorAPITimeoutError:
                self.logger.error(f'Timeout error')
                if message.retry_count >= TranslationTaskConfig.MAX_RETRIES:
                    if not task.data:
                        task.data = {}
                    task.status = TranslationTaskStatus.failed
                    task.data = 'Превышено максимальное количество попыток'
                else:
                    producer = KafkaProducer(
                        bootstrap_servers=KafkaConfig.address,
                        topic=KafkaConfig.translation_topic
                    )

                    message.retry_count += 1
                    await producer.send_message(
                        message.model_dump(mode='json')
                    )
                    task.status = TranslationTaskStatus.started
            except Exception as e:
                if not task.data:
                    task.data = {}
                task.status = TranslationTaskStatus.failed
                error_data = json.loads(str(e))
                error_message = str(e)
                if 'error' in error_data:
                    if 'message' in error_data['error']:
                        self.logger.warning(
                            f'ERROR MESSAGE: {error_data['error']['message']}'
                        )
                        if self.__error_includes(
                            substrings=['ProviderNotFound'],
                            error_data=error_data
                        ):
                            error_message = (
                                f'Модель {model.show_name} недоступна.'
                                f' Попробуйте другую'
                            )
                        elif self.__error_includes(
                            substrings=['ERR_BN_LIMIT', 'RateLimit'],
                            error_data=error_data
                        ):
                            error_message = (
                                f'Модель {model.show_name} временно '
                                f'недоступна. Попробуйте позже'
                            )
                        else:
                            error_message = error_data['error']['message']
                    else:
                        self.logger.warning(f'Unable to retrieve message'
                                            f' from error: {error_data}')
                else:
                    self.logger.warning(f'Unable to retrieve error data from'
                                        f' exception: {error_data}')
            task.data = error_message

            db_session.add(task)
            await db_session.commit()
            await db_session.refresh(task)
            await db_session.refresh(target_lang)
            await db_session.refresh(article)

            translation_error = bool(task.data)
            await send_notification(
                notification_scheme=NotificationCreateScheme(
                    title=(
                        NotificationConfig.Subjects.translation_ended
                        if not translation_error else
                        NotificationConfig.Subjects.translation_error
                    ),
                    text=(
                        NotificationConfig.translation_success_message.format(
                            article_name=article.title,
                            target_lang=target_lang.name,
                        ) if not translation_error else
                        task.data
                    ),
                    type=(
                        NotificationType.info if not translation_error else
                        NotificationType.error
                    ),
                    user_id=article.user_id
                ),
                db_session=db_session
            )
            self.logger.info('Gracefully returning')
