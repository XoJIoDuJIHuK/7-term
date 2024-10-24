import uuid

from src.database.models import ConfirmationCode, ConfirmationType
from src.settings import AppConfig

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.util.time.helpers import get_utc_now


class ConfirmationCodeRepository:
    @staticmethod
    async def get(
            value: str,
            reason: ConfirmationType,
            db_session: AsyncSession,
    ) -> ConfirmationCode | None:
        max_exp_at = get_utc_now() + AppConfig.conf_code_exp_seconds
        result = await db_session.execute(select(ConfirmationCode).where(
            ConfirmationCode.code == value,
            ConfirmationCode.reason == reason,
            ConfirmationCode.expired_at <= max_exp_at,
            ConfirmationCode.is_used.is_(False)
        ))
        return result.scalars().first()

    @staticmethod
    async def mark_as_used(
            confirmation_code: ConfirmationCode,
            db_session: AsyncSession
    ) -> None:
        confirmation_code.is_used = True
        db_session.add(confirmation_code)
        await db_session.commit()

    @staticmethod
    async def create(
            code: str,
            user_id: uuid.UUID,
            reason: ConfirmationType,
            db_session: AsyncSession
    ):
        confirmation_code = ConfirmationCode(

        )
