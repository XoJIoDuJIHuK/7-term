from fastapi import (
    Depends,
    HTTPException,
    Path,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TranslationConfig
from src.depends import get_session
from src.services.config import ConfigRepository


async def get_config(
        config_id: int = Path(),
        db_session: AsyncSession = Depends(get_session),
) -> TranslationConfig:
    config = await ConfigRepository.get_by_id(
        config_id=config_id,
        db_session=db_session
    )
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Конфиг не найден'
        )
    return config