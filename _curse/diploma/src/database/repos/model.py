from src.database.models import AIModel

from sqlalchemy import and_, delete, exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.models.schemes import (
    ModelCreateScheme,
    ModelUpdateScheme,
)


class ModelRepo:
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
    async def model_exists(
            model_data: ModelUpdateScheme,
            existing_model_id: int,
            db_session: AsyncSession
    ) -> bool:
        result = await db_session.execute(select(exists().where(
            and_(
                AIModel.id != existing_model_id,
                or_(
                    AIModel.show_name == model_data.show_name,
                    and_(
                        AIModel.name == model_data.name,
                        AIModel.provider == model_data.provider,
                    )
                )
            )

        )))
        return bool(result.scalar_one_or_none())

    @staticmethod
    async def get_list(
            db_session: AsyncSession
    ) -> list[AIModel]:
        result = await db_session.execute(select(AIModel).order_by(
            AIModel.created_at
        ))
        return list(result.scalars().all())

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
            model_data: ModelCreateScheme,
            db_session: AsyncSession
    ) -> AIModel:
        model = AIModel(**model_data.model_dump())
        db_session.add(model)
        await db_session.commit()
        await db_session.refresh(model)
        return model

    @staticmethod
    async def update(
            model: AIModel,
            new_model_data: ModelUpdateScheme,
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
