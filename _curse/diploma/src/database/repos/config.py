import logging
import uuid

from fastapi import HTTPException, status

from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TranslationConfig
from src.database.repos.prompt import PromptRepo
from src.database.repos.model import ModelRepo
from src.routers.config.schemes import (
    ConfigOutScheme,
    CreateConfigScheme,
    EditConfigScheme,
)
from src.util.db.helpers import update_object
from src.util.time.helpers import get_utc_now


logger = logging.getLogger(__name__)


def name_conflicts_error(name):
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f'Конфиг с названием {name} уже существует'
    )


class ConfigRepo:
    @staticmethod
    async def config_exists_by_name(
            name: str,
            old_config_id: int | None,
            user_id: uuid.UUID,
            db_session: AsyncSession
    ) -> bool:
        result = await db_session.execute(select(exists().where(
            TranslationConfig.user_id == user_id,
            TranslationConfig.name == name,
            TranslationConfig.id != old_config_id,
        )))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
            user_id: uuid.UUID,
            db_session: AsyncSession
    ) -> list[ConfigOutScheme]:
        result = await db_session.execute(select(TranslationConfig).where(
            TranslationConfig.user_id == user_id,
            TranslationConfig.deleted_at.is_(None)
        ).order_by(TranslationConfig.created_at))
        return [
            ConfigOutScheme.model_validate(c) for c in result.scalars().all()
        ]

    @staticmethod
    async def get_by_id(
            config_id: int,
            db_session: AsyncSession
    ) -> TranslationConfig | None:
        result = await db_session.execute(select(TranslationConfig).where(
            TranslationConfig.id == config_id,
            TranslationConfig.deleted_at.is_(None)
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
            config_data: CreateConfigScheme,
            user_id: uuid.UUID,
            db_session: AsyncSession,
    ) -> TranslationConfig:
        if await ConfigRepo.config_exists_by_name(
            name=config_data.name,
            user_id=user_id,
            old_config_id=None,
            db_session=db_session
        ):
            logger.warning(f'Config name conflict: {config_data.name}')
            result = await db_session.execute(
                delete(TranslationConfig)
                .where(
                    TranslationConfig.user_id == user_id,
                    TranslationConfig.name == config_data.name,
                    TranslationConfig.deleted_at.isnot(None)
                )
            )
            if result.rowcount == 0:
                raise name_conflicts_error(config_data.name)
            logger.info('Config name conflict resolved')
        if (
            config_data.model_id is not None
            and not await ModelRepo.exists_by_id(
                model_id=config_data.model_id,
                db_session=db_session
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Модель не найдена'
            )
        if (
            config_data.prompt_id is not None
            and not await PromptRepo.exists_by_id(
                prompt_id=config_data.prompt_id,
                db_session=db_session
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Промпт не найден'
            )
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
        if await ConfigRepo.config_exists_by_name(
            name=new_data.name,
            user_id=config.user_id,
            old_config_id=config.id,
            db_session=db_session
        ):
            raise name_conflicts_error(new_data.name)
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
        await db_session.commit()
        await db_session.refresh(config)
        return config
