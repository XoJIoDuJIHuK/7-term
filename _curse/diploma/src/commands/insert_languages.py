import asyncio
import json
import logging
import sys

import click

from src.database import get_session
from src.database.models import Language

from src.settings import LOGGER_PREFIX

from sqlalchemy.future import select

logger = logging.getLogger(LOGGER_PREFIX + __name__)


@click.command()
def insert_languages() -> None:
    with open('contrib/persistent_data/languages.json', 'r') as file:
        languages = json.load(file)

    async def async_function() -> None:
        async with get_session() as db:
            db_query = await db.execute(select(Language))
            db_languages = db_query.scalars().first()
            if db_languages:
                logger.info('There already are languages in the DB')
                return

            language_objects = [
                Language(
                    name=lang, iso_code=iso_code
                ) for lang, iso_code in languages.items()
            ]
            db.add_all(language_objects)
            await db.commit()
        logger.info('Languages inserted')
        return

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_function())
    loop.close()
    sys.exit()
