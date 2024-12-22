from typing import AsyncGenerator

from fastapi import Cookie, HTTPException, status

from src.database import get_session as get_db_session

from sqlalchemy.ext.asyncio import AsyncSession

from src.settings import Role
from src.util.auth.classes import JWTCookie
from src.util.auth.helpers import verify_jwt
from src.util.auth.schemes import UserInfo


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db_session() as session:
        yield session


async def validate_token_for_ws(
        access_token: str | None = Cookie()
) -> UserInfo:
    error_invalid_token = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Неправильные данные входа'
    )
    error_no_rights = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='Недостаточно прав'
    )
    if access_token is None or not (payload := verify_jwt(access_token)):
        raise error_invalid_token
    provided_role = payload.role
    if not JWTCookie.role_allowed([Role.user, Role.moderator], provided_role):
        raise error_no_rights

    return payload
