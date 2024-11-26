from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repos.analytics import AnalyticsRepo
from src.depends import get_session
from src.settings import Role
from src.util.auth.classes import JWTCookie
from src.util.auth.schemes import UserInfo

router = APIRouter(
    prefix='/analytics',
    tags=['Analytics']
)


@router.get(
    '/models-stats/'
)
async def get_models_info(
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin])),
        db_session: AsyncSession = Depends(get_session)
):
    return await AnalyticsRepo.get_models_stats(db_session)


@router.get(
    '/prompts-stats/'
)
async def get_models_info(
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin])),
        db_session: AsyncSession = Depends(get_session)
):
    return await AnalyticsRepo.get_prompts_stats(db_session)
