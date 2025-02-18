from pika import BlockingConnection, ConnectionParameters, credentials

from src.logger import get_logger

from src.settings import RabbitMQConfig


logger = get_logger(__name__)
rabbit_config = RabbitMQConfig()


class RabbitConsumer:
    def run(self):
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

        channel.basic_consume(
            queue='test', auto_ack=True, on_message_callback=self.on_message
        )

        channel.start_consuming()

    def on_message(self, ch, method, properties, body):
        message = ''

        logger.info('')
