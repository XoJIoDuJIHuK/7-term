import asyncio
import sys

import click

from src.consumers.translator.classes import TranslationTaskConsumer
from src.logger import get_logger
from src.settings import RabbitMQConfig
from src.util.brokers.consumer.rabbitmq import TranslationConsumer

logger = get_logger(__name__)
rabbitmq_config = RabbitMQConfig()


@click.command('start_translator_consumer')
def start_translator_consumer():
    try:
        TranslationConsumer().run(rabbitmq_config.translation_topic)
    except Exception as e:
        logger.exception(e)
