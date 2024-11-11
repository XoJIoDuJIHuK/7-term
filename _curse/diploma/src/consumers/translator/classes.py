import logging

from src.consumers.translator.schemes import TranslationMessage
from src.database import get_session
from src.events import handle_event
from src.database.models import TranslationTaskStatus
from src.routers.articles.schemes import CreateArticleScheme
from src.database.repos.article import ArticleRepo
from src.database.repos.language import LanguageRepo
from src.database.repos.model import ModelRepo
from src.database.repos.prompt import PromptRepo
from src.database.repos.translation_task import TaskRepo
from src.database.repos.user import UserRepo
from src.settings import (
    AppEvent,
    KafkaConfig,
    LOGGER_PREFIX,
    TranslationTaskConfig, UnisenderConfig,
)
from src.util.brokers.consumer.kafka import AbstractKafkaConsumer
from src.util.brokers.producer.kafka import KafkaProducer
from src.util.mail.schemes import SendEmailScheme
from src.util.translator.classes import Gpt4freeTranslator
from src.util.translator.exceptions import TranslatorAPITimeoutError


class TranslationTaskConsumer(AbstractKafkaConsumer):
    """Class that contains logic for handling Kafka consumer messages.

    Attributes:
        logger (logging.Logger): Logger instance for this class.
    """

    logger = logging.getLogger(LOGGER_PREFIX + __name__)
    translator = Gpt4freeTranslator()

    async def on_message(self, msg):
        message = TranslationMessage(**msg.value)

        async with get_session() as db_session:
            task = await TaskRepo.get_by_id(
                task_id=message.task_id,
                db_session=db_session
            )
            if not task:
                raise Exception(
                    f'Задача с идентификатором {message.task_id} не найдена'
                )

            try:
                article = await ArticleRepo.get_by_id(
                    article_id=task.article_id,
                    db_session=db_session
                )
                if not article:
                    raise Exception(
                        f'Исходная статья не найдена по идентификатору:'
                        f' {task.article_id}'
                    )
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
                        f'Исходная статья не найдена по идентификатору:'
                        f' {task.model_id}'
                    )
                model = await ModelRepo.get_by_id(
                    model_id=task.model_id,
                    db_session=db_session
                )
                if not model:
                    raise Exception(
                        f'Модель не найдена по идентификатору:'
                        f' {task.model_id}'
                    )
                prompt_object = await PromptRepo.get_by_id(
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

                translated_title = await self.translator.translate(
                    text=article.title,
                    target_language=target_lang,
                    source_language=source_lang if source_lang else None,
                    model=model,
                    prompt_object=prompt_object
                )

                translated_text = await self.translator.translate(
                    text=article.text,
                    target_language=target_lang,
                    source_language=source_lang if source_lang else None,
                    model=model,
                    prompt_object=prompt_object
                )

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

                producer = KafkaProducer(
                    bootstrap_servers=KafkaConfig.address,
                    topic=KafkaConfig.mail_topic
                )
                user = await UserRepo.get_by_id(
                    user_id=article.user_id,
                    db_session=db_session
                )
                kafka_message = SendEmailScheme(
                    to_address=user.email,
                    from_address=UnisenderConfig.from_address,
                    from_name=UnisenderConfig.from_name,
                    subject=UnisenderConfig.email_confirmation_subject,
                    template_id=UnisenderConfig.email_confirmation_template_id,
                    params={
                        'article_title': article.title,
                        'translated_article_title': translated_article.title
                    }
                )
                # TODO: add notification
                await producer.send_message(
                    kafka_message.model_dump(mode='json'))

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
