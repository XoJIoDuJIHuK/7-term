import uuid

from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TranslationConfig
from src.routers.config.schemes import (
    ConfigOutScheme,
    CreateConfigScheme,
    EditConfigScheme,
)
from src.util.db.helpers import update_object
from src.util.time.helpers import get_utc_now


name_conflicts_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail='Конфиг с таким названием уже существует'
)


class ConfigRepository:
    @staticmethod
    async def config_exists_by_name(
            name: str,
            user_id: uuid.UUID,
            db_session: AsyncSession
    ) -> bool:
        result = await db_session.execute(select(exists().where(
            TranslationConfig.user_id == user_id,
            TranslationConfig.name == name
        )))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
            user_id: uuid.UUID,
            db_session: AsyncSession
    ) -> list[ConfigOutScheme]:
        result = await db_session.execute(select(TranslationConfig).filter_by(
            user_id=user_id
        ))
        return [
            ConfigOutScheme.model_validate(c) for c in result.scalars().all()
        ]

    @staticmethod
    async def get_by_id(
            config_id: int,
            db_session: AsyncSession
    ) -> TranslationConfig | None:
        result = await db_session.execute(select(TranslationConfig).filter_by(
            id=config_id
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
            config_data: CreateConfigScheme,
            user_id: uuid.UUID,
            db_session: AsyncSession,
    ) -> TranslationConfig:
        if await ConfigRepository.config_exists_by_name(
            name=config_data.name,
            user_id=user_id,
            db_session=db_session
        ):
            raise name_conflicts_error
        config = TranslationConfig(
            user_id=user_id,
            name=config_data.name,
            prompt_id=config_data.prompt_id,
            language_ids=config_data.language_ids,
            model_id=config_data.model_id
        )
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)
        return config

    @staticmethod
    async def update(
            config: TranslationConfig,
            new_data: EditConfigScheme,
            db_session: AsyncSession
    ) -> TranslationConfig:
        if await ConfigRepository.config_exists_by_name(
            name=new_data.name,
            user_id=config.user_id,
            db_session=db_session
        ):
            raise name_conflicts_error
        config = update_object(
            db_object=config,
            update_scheme=new_data
        )
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)
        return config

    @staticmethod
    async def delete(
            config: TranslationConfig,
            db_session: AsyncSession
    ) -> TranslationConfig:
        config.deleted_at = get_utc_now()
        db_session.add(config)
        await db_session.commit()
        await db_session.refresh(config)
        return config
