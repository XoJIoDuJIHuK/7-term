from abc import ABC, abstractmethod


class AbstractConsumer(ABC):
    """Abstract class for consumer."""

    @abstractmethod
    async def run(self):
        """Abstract method to run consumer.

        This method must be implemented by subclasses to provide
        the specific logic for consumer.
        """
        pass

    @abstractmethod
    async def on_message(self, msg):
        """Abstract method to get messages.

        This method must be implemented by subclasses to provide
        the specific logic for consumer.
        """
        pass
