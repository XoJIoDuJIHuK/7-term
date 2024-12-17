from fastapi import HTTPException, status

from src.database.repos.model import ModelRepo

from sqlalchemy.ext.asyncio import AsyncSession

from src.routers.models.schemes import ModelUpdateScheme, ModelCreateScheme


async def check_model_conflicts(
        model_data: ModelUpdateScheme | ModelCreateScheme,
        existing_model_id: int | None,
        db_session: AsyncSession
):
    if await ModelRepo.model_exists(
        model_data=model_data,
        existing_model_id=existing_model_id,
        db_session=db_session
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Модель от данного провайдера с таким именем уже существует'
        )
