from fastapi import HTTPException, status

from src.services.model import ModelRepository

from sqlalchemy.ext.asyncio import AsyncSession


async def check_model_conflicts(
        name: str,
        provider: str,
        db_session: AsyncSession
):
    if await ModelRepository.exists_by_name_and_provider(
        name=name,
        provider=provider,
        db_session=db_session
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Модель от данного провайдера с таким именем уже существует'
        )
