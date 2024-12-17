import json
from typing import Any, List

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.logger import get_logger


class KafkaProducer:
    """ A class for working with Kafka, implementing methods for connecting,
        sending messages, and managing the lifecycle of a Kafka producer.
    """
    def __init__(
            self,
            bootstrap_servers: Any,
            topic: Any
    ):
        """
        Initializes the KafkaProducer with the specified Kafka bootstrap
        servers, topic, and transactional ID.

        Parameters:
        bootstrap_servers(Any) : The Kafka server addresses to connect to.
        topic(Any) : The Kafka topic where messages will be sent.
        """
        self.topic = topic
        self.producer = None
        self.bootstrap_servers = bootstrap_servers
        self.logger = get_logger(__name__)

    async def connect(self):
        """
        Establishes a connection to Kafka and initializes the producer.
        """
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except Exception as e:
            self.logger.error(f'Error connecting to Kafka: {e}')

    async def start(self):
        """
        Starts the Kafka producer.
        """
        try:
            await self.producer.start()
        except Exception as e:
            self.logger.error(f'Error starting Kafka producer: {e}')

    async def reconnect(self):
        """
        Reconnects to Kafka.
        """
        try:
            if self.producer:
                await self.stop()
                self.producer = None
            await self.connect()
        except Exception as e:
            self.logger.error(f'Error reconnecting to Kafka: {e}')

    async def stop(self):
        """
        Stops the Kafka producer.
        """
        try:
            await self.producer.stop()
        except Exception as e:
            self.logger.error(f'Error stopping Kafka producer: {e}')

    async def begin_transaction(self):
        """
        Begins a new Kafka transaction.
        """
        try:
            await self.producer.begin_transaction()
        except KafkaError as e:
            self.logger.error(f'Error beginning Kafka transaction: {e}')
            raise

    async def commit_transaction(self):
        """
        Commits the Kafka transaction.
        """
        try:
            await self.producer.commit_transaction()
        except KafkaError as e:
            self.logger.error(f'Error committing Kafka transaction: {e}')
            raise

    async def abort_transaction(self):
        """
        Aborts the Kafka transaction.
        """
        try:
            await self.producer.abort_transaction()
        except KafkaError as e:
            self.logger.error(f'Error aborting Kafka transaction: {e}')
            raise

    async def send_message(self, message: dict):
        try:
            await self.connect()
            await self.start()
            await self.producer.send_and_wait(self.topic, value=message)
        except Exception as e:
            self.logger.error(f'Error sending message to Kafka: {e}')
        finally:
            await self.stop()

    async def send_messages(self, messages: List[dict]):
        try:
            await self.connect()
            await self.start()

            for message in messages:
                await self.producer.send_and_wait(self.topic, value=message)
        except Exception as e:
            self.logger.error(
                f'Error sending messages to Kafka: {e}'
            )
            raise
        finally:
            await self.stop()
