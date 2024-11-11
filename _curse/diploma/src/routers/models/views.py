from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status, Path,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.depends import get_session
from src.http_responses import get_responses
from src.responses import DataResponse, BaseResponse, \
    SimpleListResponse
from src.routers.models.helpers import check_model_conflicts
from src.routers.models.schemes import ModelOutScheme, CreateModelScheme, \
    UpdateModelScheme, ModelAdminOutScheme
from src.database.repos.model import ModelRepo
from src.settings import Role
from src.util.auth.classes import JWTCookie
from src.util.auth.schemes import UserInfo

router = APIRouter(
    prefix='/models',
    tags=['Models']
)


@router.get(
    '/',
    response_model=SimpleListResponse[ModelOutScheme],
)
async def get_models(
        db_session: AsyncSession = Depends(get_session)
):
    return SimpleListResponse[ModelOutScheme].from_list(
        items=[
            ModelOutScheme.model_validate(m) for m
            in await ModelRepo.get_list(db_session)
        ]
    )


@router.get(
    '/admin/',
    response_model=SimpleListResponse[ModelAdminOutScheme]
)
async def get_admin_models(
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin]))
):
    return SimpleListResponse[ModelAdminOutScheme].from_list(
        items=[
            ModelAdminOutScheme.model_validate(m) for m
            in await ModelRepo.get_list(db_session)
        ]
    )


@router.post(
    '/',
    response_model=DataResponse.single_by_key(
        'model',
        ModelOutScheme
    ),
    responses=get_responses(400, 401, 403, 409)
)
async def create_model(
        model_data: CreateModelScheme,
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin]))
):
    await check_model_conflicts(
        name=model_data.name,
        provider=model_data.provider,
        db_session=db_session
    )
    model = await ModelRepo.create(
        model_data=model_data,
        db_session=db_session
    )
    return DataResponse(
        data={
            'model': ModelOutScheme.model_validate(model)
        }
    )


@router.put(
    '/{model_id}/',
    response_model=DataResponse.single_by_key(
        'model',
        ModelOutScheme
    ),
    responses=get_responses(400, 401, 403, 404, 409)
)
async def update_model(
        model_data: UpdateModelScheme,
        model_id: int = Path(),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin]))
):
    model = await ModelRepo.get_by_id(
        model_id=model_id,
        db_session=db_session
    )
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Модели не существует'
        )
    await check_model_conflicts(
        name=model_data.name,
        provider=model_data.provider,
        db_session=db_session
    )
    model = await ModelRepo.update(
        model=model,
        new_model_data=model_data,
        db_session=db_session
    )
    return DataResponse(
        data={
            'model': ModelOutScheme.model_validate(model)
        }
    )


@router.delete(
    '/{model_id}/',
    response_model=BaseResponse,
    responses=get_responses(400, 401, 403, 404)
)
async def delete_model(
        model_id: int = Path(),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin]))
):
    result = await ModelRepo.delete(
        model_id=model_id,
        db_session=db_session
    )
    return BaseResponse(message=result)
