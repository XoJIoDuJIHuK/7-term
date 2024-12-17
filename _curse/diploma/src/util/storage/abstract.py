from abc import ABC, abstractmethod
from typing import Optional


class AbstractStorage(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[dict]:
        """
        Retrieves a dictionary value from storage for the given key.

        Args:
            key: A string key to look up the value.

        Returns:
            The dictionary value associated with the key, or None if the key
                doesn't exist.

        """
        pass

    @abstractmethod
    async def set(self, key: str, value: dict) -> None:
        """
        Sets a dictionary value in storage for the given key.

        Args:
            key: A string key under which to store the value.
            value: The dictionary value to store.
        """
        pass
