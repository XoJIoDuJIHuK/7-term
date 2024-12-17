from src.logger import get_logger
from src.settings import LOGGER_PREFIX
from src.util.brokers.consumer.kafka import AbstractKafkaConsumer
from src.util.mail.classes import UnisenderMailSender
from src.util.mail.schemes import SendEmailScheme


class EmailTaskConsumer(AbstractKafkaConsumer):
    logger = get_logger(LOGGER_PREFIX + __name__)

    async def on_message(self, msg):
        message = SendEmailScheme(**msg.value)
        self.logger.info(
            f'Sending {message.subject} email to {message.to_address}'
        )
        try:
            await UnisenderMailSender.send(
                to_address=message.to_address,
                from_address=message.from_address,
                from_name=message.from_name,
                subject=message.subject,
                template_id=message.template_id,
                params=message.params,
            )
            self.logger.warning(f'Message to {message.to_address} is sent')
            self.logger.info(f'Message sent successfully')
        except Exception as e:
            self.logger.exception(e)
