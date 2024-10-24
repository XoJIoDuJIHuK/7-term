import asyncio
import sys


import click

from src.consumers.mail.unisender import EmailTaskConsumer
from src.settings import KafkaConfig


@click.command('start_mail_consumer')
def start_mail_consumer():
    consumer = EmailTaskConsumer(
        topic=KafkaConfig.mail_topic,
        bootstrap_servers=KafkaConfig.address,
        group_id=KafkaConfig.translation_topic,
        auto_offset_reset='latest'
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(consumer.run())
    loop.close()
    sys.exit()
