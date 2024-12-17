import json
from abc import abstractmethod
from typing import Any

from aiokafka import AIOKafkaConsumer

from src.logger import get_logger
from src.settings import LOGGER_PREFIX, KafkaConfig
from src.util.brokers.consumer.abstract import AbstractConsumer


class AbstractKafkaConsumer(AbstractConsumer):
    """Abstract base class for Kafka consumers.

    This class provides the basic functionality for connecting to and consuming
    messages from a Kafka topic.
    Subclasses should implement the `on_message` method to define how messages
    are processed.
    """

    logger = get_logger(LOGGER_PREFIX + __name__)

    def __init__(
            self,
            topic: Any,
            bootstrap_servers: Any,
            group_id: str,
            auto_offset_reset: str
    ):
        """Initializes the Kafka consumer with the given configuration.

        Args:
            topic (Any): The topic to consume messages from.
            bootstrap_servers (Any): The Kafka bootstrap servers.
            group_id (str): The consumer group ID.
            auto_offset_reset (str): The offset reset policy ('earliest' or
            'latest').
        """
        self.consumer = None
        self.topic = topic
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.auto_offset_reset = auto_offset_reset

    async def run(self):
        """Runs the Kafka consumer, connecting to Kafka and starting message
        consumption.
        """
        try:
            self.logger.info('Running KafkaConsumer...')
            await self.connect()
            await self.start()
            self.logger.info('Connection successful!')
            self.logger.info('Searching for messages...')
            async for msg in self.consumer:
                await self.on_message(msg)
        except Exception as e:
            self.logger.exception(f'Error while running Kafka consumer: {e}')
            await self.stop()

    async def connect(self):
        """Connects to the Kafka broker and initializes the consumer."""
        try:
            self.logger.info('Connecting to KafkaConsumer...')
            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                max_poll_interval_ms=KafkaConfig.max_poll_interval_ms
            )
        except Exception as e:
            self.logger.error(f'Error while connecting to Kafka: {e}')

    async def reconnect(self):
        """Reconnects to the Kafka broker, stopping the current consumer
        if necessary.
        """
        try:
            if self.consumer:
                await self.stop()
                self.consumer = None
            await self.connect()
        except Exception as e:
            self.logger.error(f'Error while reconnecting to Kafka: {e}')

    async def start(self):
        """Starts the Kafka consumer to begin consuming messages."""
        try:
            await self.consumer.start()
        except Exception as e:
            self.logger.error(f'Error while starting Kafka consumer: {e}')

    async def stop(self):
        """Stops the Kafka consumer."""
        try:
            await self.consumer.stop()
        except Exception as e:
            self.logger.error(f'Error while stopping Kafka consumer: {e}')

    @abstractmethod
    async def on_message(self, msg):
        """Handles an incoming Kafka message.

        Args:
            msg: The message received from Kafka.

        This method should be implemented by subclasses to define custom
        message handling logic.
        """
        pass
