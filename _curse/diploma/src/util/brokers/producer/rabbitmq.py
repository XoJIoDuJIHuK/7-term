import json
from pika import BlockingConnection, ConnectionParameters, credentials
from src.logger import get_logger
from src.settings import RabbitMQConfig

logger = get_logger(__name__)
rabbit_config = RabbitMQConfig()


def publish_message(routing_key: str, message: dict):
    connection = BlockingConnection(
        ConnectionParameters(
            rabbit_config.host,
            credentials=credentials.PlainCredentials(
                rabbit_config.login, rabbit_config.password
            ),
        )
    )
    channel = connection.channel()
    channel.queue_declare(routing_key)
    channel.basic_publish('', routing_key, json.dumps(message))
    logger.info('Message %s was sent to queue %s', message, routing_key)
    connection.close()
