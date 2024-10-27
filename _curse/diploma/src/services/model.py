from src.database.models import AIModel

from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.models.schemes import ModelOutScheme, CreateModelScheme, \
    UpdateModelScheme


class ModelRepository:
    @staticmethod
    async def exists_by_id(
            model_id: int,
            db_session: AsyncSession
    ) -> bool:
        result = await db_session.execute(select(exists().where(
            AIModel.id == model_id
        )))
        return result.scalar_one_or_none()

    @staticmethod
    async def exists_by_name_and_provider(
            name: str,
            provider: str,
            db_session: AsyncSession
    ) -> bool:
        result = await db_session.execute(select(exists().where(
            AIModel.name == name,
            AIModel.provider == provider
        )))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
            db_session: AsyncSession
    ) -> list[ModelOutScheme]:
        result = await db_session.execute(select(AIModel))
        return [
            ModelOutScheme.model_validate(m) for m in result.scalars().all()
        ]

    @staticmethod
    async def get_by_id(
            model_id: int,
            db_session: AsyncSession
    ) -> AIModel | None:
        result = await db_session.execute(select(AIModel).where(
            AIModel.id == model_id,
            AIModel.deleted_at.is_(None)
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
            model_data: CreateModelScheme,
            db_session: AsyncSession
    ) -> AIModel:
        model = AIModel(
            name=model_data.name,
            provider=model_data.provider,
        )
        db_session.add(model)
        await db_session.commit()
        await db_session.refresh(model)
        return model

    @staticmethod
    async def update(
            model: AIModel,
            new_model_data: UpdateModelScheme,
            db_session: AsyncSession
    ) -> AIModel:
        for key, value in vars(new_model_data).items():
            if value is not None:
                model.__setattr__(key, value)
        db_session.add(model)
        await db_session.commit()
        await db_session.refresh(model)
        return model

    @staticmethod
    async def delete(
            model_id: int,
            db_session: AsyncSession
    ):
        result = await db_session.execute(delete(AIModel).where(
            AIModel.id == model_id
        ))
        return result.scalar_one_or_none()
