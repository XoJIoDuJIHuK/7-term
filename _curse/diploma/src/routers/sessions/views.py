import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.depends import get_session
from src.http_responses import get_responses
from src.pagination import get_pagination_params, PaginationParams
from src.responses import ListResponse, BaseResponse
from src.routers.sessions.schemes import (
    SessionOutScheme,
)
from src.services.session import SessionRepository
from src.util.auth.classes import JWTBearer
from src.util.auth.helpers import put_tokens_in_black_list
from src.util.auth.schemes import UserInfo
from src.util.common.schemes import SuccessResponse
from src.util.storage.classes import RedisHandler

router = APIRouter(
    prefix='/sessions',
    tags=['Sessions']
)


@router.get(
    '/sessions/',
    response_model=ListResponse[SessionOutScheme],
    responses=get_responses(400, 401)
)
async def get_sessions(
        user_info: UserInfo = Depends(JWTBearer()),
        db_session: AsyncSession = Depends(get_session),
        pagination: PaginationParams = Depends(get_pagination_params)
):
    sessions, count = await SessionRepository.get_list(
        user_id=user_info.id,
        pagination_params=pagination,
        db_session=db_session
    )
    return ListResponse[SessionOutScheme].from_list(
        items=sessions,
        total_count=count,
        params=pagination
    )


@router.post(
    '/sessions/close/',
    response_model=BaseResponse,
    responses=get_responses(400, 401)
)
async def close_sessions(
        user_info: UserInfo = Depends(JWTBearer()),
        db_session: AsyncSession = Depends(get_session),
):
    refresh_token_ids = await SessionRepository.get_refresh_token_ids(
        user_id=user_info.id,
        db_session=db_session
    )
    put_tokens_in_black_list(refresh_token_ids)
    await SessionRepository.close_all(
        user_id=user_info.id,
        db_session=db_session
    )
    return BaseResponse(message='Все сессии успешно закрыты')
