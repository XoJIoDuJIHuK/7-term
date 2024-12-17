import asyncio
import json
import sys

import click

from src.database import get_session
from src.database.models import AIModel
from src.logger import get_logger
from src.settings import LOGGER_PREFIX

from sqlalchemy.future import select

logger = get_logger(LOGGER_PREFIX + __name__)


@click.command()
def insert_models() -> None:
    with open('contrib/persistent_data/models.json', 'r') as file:
        models = json.load(file)

    async def async_function() -> None:
        async with get_session() as db:
            db_query = await db.execute(select(AIModel))
            db_models = db_query.scalars().all()

            model_objects = [
                AIModel(
                    show_name=arr[0], name=arr[1], provider=arr[2]
                ) for arr in models
                if arr[0] not in map(lambda x: x.show_name, db_models)
            ]
            if model_objects:
                logger.info(f'Inserting models {[
                    model.show_name for model in model_objects
                ]}')
                db.add_all(model_objects)
                await db.commit()
            else:
                logger.info('No models to insert')
        return

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_function())
    loop.close()
    sys.exit()
