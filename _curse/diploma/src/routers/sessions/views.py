from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from fastapi_pagination import Params

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.routers.sessions.schemes import (
    SessionOutScheme,
)
from src.services.session import SessionRepository
from src.util.auth.classes import JWTBearer
from src.util.auth.schemes import UserInfo
from src.util.common.schemes import SuccessResponse


router = APIRouter(
    prefix='/sessions',
    tags=['Sessions']
)


@router.get(
    '/sessions/'
)
async def get_sessions(
        user_info: UserInfo = Depends(JWTBearer()),
        db_session: AsyncSession = Depends(get_session),
        pagination_params: Params = Depends()
):
    aga = await SessionRepository.get_list(
        user_id=user_info.id,
        pagination_params=pagination_params,
        db_session=db_session
    )
    aga.items = [SessionOutScheme.model_validate(i) for i in aga.items]
    print(aga.items)
    return aga


@router.post(
    '/sessions/close/'
)
async def close_sessions(
        user_info: UserInfo = Depends(JWTBearer),
        db_session: AsyncSession = Depends(get_session),
):
    await SessionRepository.close_all(
        user_id=user_info.id,
        db_session=db_session
    )
    return SuccessResponse(message='Все сессии успешно закрыты')