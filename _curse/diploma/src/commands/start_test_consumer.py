import asyncio
import sys

import click

from src.logger import get_logger
from src.util.brokers.consumer.rabbitmq import RabbitConsumer

logger = get_logger(__name__)


@click.command("start_test_consumer")
def start_test_consumer():
    try:
        RabbitConsumer().run()
    except Exception as e:
        logger.exception(e)
