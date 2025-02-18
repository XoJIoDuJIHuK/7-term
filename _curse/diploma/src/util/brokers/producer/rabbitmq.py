from pika import BlockingConnection, ConnectionParameters, credentials

from src.settings import RabbitMQConfig
import os

print('THE ADDRESS IS', os.getenv('RABBIT_HOST'))
rabbit_config = RabbitMQConfig()


def publish_hello_world():
    connection = BlockingConnection(
        ConnectionParameters(
            rabbit_config.host,
            credentials=credentials.PlainCredentials(
                rabbit_config.login, rabbit_config.password
            ),
        )
    )
    channel = connection.channel()
    channel.queue_declare('test')
    channel.basic_publish('', 'test', 'Hello, World!')
    print('Hello World was published to the queue')
    connection.close()
