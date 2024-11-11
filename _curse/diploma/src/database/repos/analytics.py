from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import(
    AIModel,
    Report,
    ReportReason,
    ReportStatus,
)


class AnalyticsRepo:
    @staticmethod
    async def get(
            db_session: AsyncSession
    ):
        query = select(AIModel, )