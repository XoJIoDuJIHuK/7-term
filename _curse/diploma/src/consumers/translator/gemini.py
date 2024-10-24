import logging

from src.consumers.translator.schemes import TranslationMessage
from src.database import get_session
from src.events import handle_event
from src.database.models import TranslationTaskStatus
from src.routers.articles.schemes import CreateArticleScheme
from src.services.article import ArticleRepository
from src.services.language import LanguageRepository
from src.services.model import ModelRepository
from src.services.prompt import PromptRepository
from src.services.translation_task import TaskRepository
from src.settings import (
    AppEvent,
    KafkaConfig,
    LOGGER_PREFIX,
    TranslationTaskConfig,
)
from src.util.brokers.consumer.kafka import AbstractKafkaConsumer
from src.util.brokers.producer.kafka import KafkaProducer
from src.util.translator.classes import GeminiTranslator
from src.util.translator.exceptions import TranslatorAPITimeoutError


class TranslationTaskConsumer(AbstractKafkaConsumer):
    """Class that contains logic for handling Kafka consumer messages.

    Attributes:
        logger (logging.Logger): Logger instance for this class.
    """

    logger = logging.getLogger(LOGGER_PREFIX + __name__)

    async def on_message(self, msg):
        message = TranslationMessage(**msg.value)

        async with get_session() as db_session:
            task = await TaskRepository.get_by_id(
                task_id=message.task_id,
                db_session=db_session
            )
            if not task:
                raise Exception(
                    f'Задача с идентификатором {message.task_id} не найдена'
                )

            try:
                article = await ArticleRepository.get_by_id(
                    article_id=task.article_id,
                    db_session=db_session
                )
                if not article:
                    raise Exception(
                        f'Исходная статья не найдена по идентификатору:'
                        f' {task.article_id}'
                    )
                source_lang = await LanguageRepository.get_by_id(
                    language_id=task.source_language_id,
                    db_session=db_session
                )
                target_lang = await LanguageRepository.get_by_id(
                    language_id=task.target_language_id,
                    db_session=db_session
                )
                if not target_lang:
                    raise Exception(
                        f'Исходная статья не найдена по идентификатору:'
                        f' {task.model_id}'
                    )
                model = await ModelRepository.get_by_id(
                    model_id=task.model_id,
                    db_session=db_session
                )
                if not model:
                    raise Exception(
                        f'Модель не найдена по идентификатору:'
                        f' {task.model_id}'
                    )
                prompt_object = await PromptRepository.get_by_id(
                    prompt_id=task.prompt_id,
                    db_session=db_session
                )
                if not prompt_object:
                    raise Exception(
                        f'Промпт не найден по идентификатору: {task.prompt_id}'
                    )

                task.status = TranslationTaskStatus.started
                db_session.add(task)
                await db_session.flush()

                translator = GeminiTranslator()

                translated_title = await translator.translate(
                    text=article.title,
                    target_language=target_lang,
                    source_language=source_lang if source_lang else None,
                    model=model,
                    prompt_object=prompt_object
                )

                translated_text = await translator.translate(
                    text=article.text,
                    target_language=target_lang,
                    source_language=source_lang if source_lang else None,
                    model=model,
                    prompt_object=prompt_object
                )

                translated_article = await ArticleRepository.create(
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
                db_session.flush()
                # TODO: add notification
                await db_session.refresh(translated_article)

                task.status = TranslationTaskStatus.completed
                task.translation_article_id = translated_article.id
                db_session.add(task)
                await db_session.commit()
            except TranslatorAPITimeoutError:
                if message.retry_count >= TranslationTaskConfig.MAX_RETRIES:
                    if not task.data:
                        task.data = {}
                    task.status = TranslationTaskStatus.failed
                    task.data['error'] = (
                        'Превышено максимальное количество попыток'
                    )
                    db_session.add(task)
                    await db_session.commit()
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
                task.data['error'] = str(e)
                db_session.add(task)
                await db_session.commit()

        await handle_event(AppEvent.translation_end.value, task=task)
