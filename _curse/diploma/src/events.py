import logging
from typing import Callable

from src.settings import LOGGER_PREFIX

_event_list = {}

logger = logging.getLogger(LOGGER_PREFIX + __name__)


def get_event_handlers(event: str) -> list[Callable]:
    return _event_list[event]


def has_registered_handlers(event: str) -> bool:
    return event in _event_list


async def handle_event(event: str, *args, **kwargs) -> None:
    if not has_registered_handlers(event):
        logger.error(f'No handlers registered for event: {event}')
        return

    handlers = get_event_handlers(event)

    for handler in handlers:
        try:
            logger.info(
                f'Executing handler {handler.__name__} for event: {event}'
            )
            await handler(event, *args, **kwargs)
        except Exception as e:
            logger.exception(
                f'Error executing handler {handler.__name__} for event '
                f'{event}: {e}'
            )


def subscribe(event: str):
    def decorator(func):
        if callable(func):
            _event_list.setdefault(event, []).append(func)
            return func
        else:
            raise Exception(f'Attempt to decorate non-callable object {func}')

    return decorator
