from src.database.models import ConfirmationCode
from src.settings import AppConfig

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.util.time.helpers import get_utc_now


class ConfirmationCodeRepository:
    @staticmethod
    async def get_by_value(
            value: str,
            db_session: AsyncSession
    ) -> ConfirmationCode | None:
        max_exp_at = get_utc_now() + AppConfig.conf_code_exp_seconds
        result = await db_session.execute(select(ConfirmationCode).where(
            ConfirmationCode.code == value,
            ConfirmationCode.expired_at <= max_exp_at,
            ConfirmationCode.is_used.is_(False)
        ))
        return result.scalars().first()
