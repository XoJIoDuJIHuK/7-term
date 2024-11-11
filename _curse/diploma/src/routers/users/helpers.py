import uuid

from fastapi import (
    Depends,
    HTTPException,
    Path,
    status,
)

from src.depends import get_session
from src.database.repos.user import UserRepo

from sqlalchemy.ext.asyncio import AsyncSession


async def get_user(
        db_session: AsyncSession = Depends(get_session),
        user_id: uuid.UUID = Path(),
):
    user = await UserRepo.get_by_id(user_id, db_session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден'
        )
    return user
