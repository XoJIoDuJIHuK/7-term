import time
import uuid
from datetime import timedelta, datetime

from src.database.models import ConfirmationCode, ConfirmationType
from src.settings import AppConfig

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.util.common.helpers import generate_random_string
from src.util.time.helpers import get_utc_now


class ConfirmationCodeRepository:
    @staticmethod
    async def get(
            value: str,
            reason: ConfirmationType,
            db_session: AsyncSession,
    ) -> ConfirmationCode | None:
        max_exp_at = datetime.fromtimestamp(
            int(time.time()) + AppConfig.conf_code_exp_seconds
        )
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

    @classmethod
    async def create(
            cls,
            user_id: uuid.UUID,
            reason: ConfirmationType,
            db_session: AsyncSession
    ):
        length = 10
        value = generate_random_string(length)
        while await cls.get(
            value=value,
            reason=reason,
            db_session=db_session
        ):
            value = generate_random_string(length)
        expired_at = (
            get_utc_now() + timedelta(seconds=AppConfig.conf_code_exp_seconds)
        )
        confirmation_code = ConfirmationCode(
            code=value,
            reason=reason,
            user_id=user_id,
            expired_at=expired_at
        )
        db_session.add(confirmation_code)
        await db_session.commit()
        await db_session.refresh(confirmation_code)
        return confirmation_code
