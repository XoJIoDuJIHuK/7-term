import asyncio
import sys


import click

from src.consumers.translator.gemini import TranslationTaskConsumer
from src.settings import KafkaConfig


@click.command('start_translator_consumer')
def start_translator_consumer():
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
