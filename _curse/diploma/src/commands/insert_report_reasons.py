import asyncio
import json
import sys

import click

from src.database import get_session
from src.database.models import ReportReason
from src.logger import get_logger
from src.settings import LOGGER_PREFIX

from sqlalchemy.future import select

logger = get_logger(LOGGER_PREFIX + __name__)


@click.command()
def insert_report_reasons() -> None:
    with open('contrib/persistent_data/report-reasons.json', 'r') as file:
        reasons = json.load(file)

    async def async_function() -> None:
        async with get_session() as db:
            db_query = await db.execute(select(ReportReason))
            db_languages = db_query.scalars().all()

            reason_objects = [
                ReportReason(
                    # id=reason.get('id'),
                    text=reason.get('text'),
                    order_position=reason.get('order_position')
                ) for reason in reasons
                if reason.get('text') not in map(
                    lambda x: x.text, db_languages
                )
            ]
            if reason_objects:
                logger.info(f'Inserting models {[
                    reason.text for reason in reason_objects
                ]}')
                db.add_all(reason_objects)
                await db.commit()
            else:
                logger.info('No report reasons to insert')
        return

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_function())
    loop.close()
    sys.exit()
