import asyncio
import sys

import click

from src.consumers.translator.classes import TranslationTaskConsumer
from src.logger import get_logger
from src.settings import KafkaConfig


logger = get_logger(__name__)


@click.command('start_translator_consumer')
def start_translator_consumer():
    try:
        consumer = TranslationTaskConsumer(
            topic=KafkaConfig.translation_topic,
            bootstrap_servers=KafkaConfig.address,
            group_id=KafkaConfig.translation_topic,
            auto_offset_reset='latest'
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(consumer.run())
        loop.close()
        sys.exit()
    except Exception as e:
        logger.exception(e)
