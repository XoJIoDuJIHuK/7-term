import asyncio
import json
import logging
import sys

import click

from src.database import get_session
from src.database.models import ReportReason

from src.settings import LOGGER_PREFIX

from sqlalchemy.future import select

logger = logging.getLogger(LOGGER_PREFIX + __name__)


@click.command()
def insert_report_reasons() -> None:
    with open('contrib/persistent_data/report-reasons.json', 'r') as file:
        reasons = json.load(file)

    async def async_function() -> None:
        async with get_session() as db:
            db_query = await db.execute(select(ReportReason))
            db_languages = db_query.scalars().first()
            if db_languages:
                logger.warning('There already are report reasons in the DB')
                return

            reason_objects = [
                ReportReason(
                    id=reason.get('id'),
                    text=reason.get('text'),
                    order_position=reason.get('order_position')
                ) for reason in reasons
            ]
            db.add_all(reason_objects)
            await db.commit()
        logger.warning('Report reasons inserted')
        return

    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_function())
    loop.close()
    sys.exit()
