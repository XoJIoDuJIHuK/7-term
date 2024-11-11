import uuid

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status, Path,
)

from src.depends import get_session
from src.database.models import User
from src.http_responses import get_responses
from src.pagination import PaginationParams, get_pagination_params
from src.responses import DataResponse, ListResponse, BaseResponse
from src.routers.users.helpers import get_user
from src.routers.users.schemes import (
    CreateUserScheme,
    FilterUserScheme,
    UserOutAdminScheme,
    UserOutScheme, EditUserScheme,
)
from src.database.repos.user import UserRepo
from src.settings import Role
from src.util.auth.classes import JWTCookie
from src.util.auth.schemes import UserInfo

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get(
    '/me/',
    response_model=DataResponse.single_by_key(
        'user',
        UserOutScheme
    ),
    responses=get_responses(400, 401)
)
async def get_my_info(
        user_info: UserInfo = Depends(JWTCookie()),
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepo.get_by_id(
        user_id=user_info.id,
        db_session=db_session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь не найден'
        )
    return DataResponse(
        data={
            'user': UserOutScheme.model_validate(user)
        }
    )


@router.get(
    '/',
    response_model=ListResponse[UserOutScheme],
    responses=get_responses(400, 401)
)
async def get_list(
        filter_email_verified: bool | None = None,
        filter_role: Role | None = None,
        pagination: PaginationParams = Depends(get_pagination_params),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin])),
        db_session: AsyncSession = Depends(get_session),
):
    users, count = await UserRepo.get_list(
        pagination_params=pagination,
        filter_params=FilterUserScheme(
            email_verified=filter_email_verified,
            role=filter_role
        ),
        db_session=db_session
    )
    return ListResponse[UserOutScheme].from_list(
        items=users,
        total_count=count,
        params=pagination
    )


@router.patch(
    '/{user_id}/name/',
    response_model=BaseResponse,
    responses=get_responses(400, 401, 409)
)
async def change_name(
        user_id: uuid.UUID = Path(),
        new_name: str = Form(min_length=1, max_length=20),
        user_info: UserInfo = Depends(JWTCookie()),
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepo.get_by_id(
        user_id=user_info.id,
        db_session=db_session
    )
    if not user or user_id != user_info.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь не найден'
        )
    if user.name == new_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Новое имя не должно совпадать со старым'
        )
    user.name = new_name
    db_session.add(user)
    await db_session.commit()
    return BaseResponse(message='Имя успешно изменено')


@router.post(
    '/',
    response_model=DataResponse.single_by_key(
        'user',
        UserOutScheme
    ),
    responses=get_responses(400, 401, 403, 409)
)
async def create_user(
        new_user_data: CreateUserScheme,
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin])),
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepo.create(
        user_data=new_user_data,
        db_session=db_session
    )
    return DataResponse(
        data={
            'user': UserOutAdminScheme.model_validate(user)
        }
    )


@router.put(
    '/{user_id}/',
    response_model=DataResponse.single_by_key(
        'user',
        UserOutScheme
    ),
    responses=get_responses(400, 401, 403, 409)
)
async def update_user(
        new_user_info: EditUserScheme,
        user: User = Depends(get_user),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin])),
        db_session: AsyncSession = Depends(get_session),
):
    user = await UserRepo.update(
        user=user,
        new_data=new_user_info,
        db_session=db_session
    )
    return DataResponse(
        data={
            'user': UserOutAdminScheme.model_validate(user)
        }
    )


@router.delete(
    '/{user_id}/',
    response_model=DataResponse.single_by_key(
        'user',
        UserOutScheme
    ),
    responses=get_responses(400, 401, 403, 409)
)
async def delete_user(
        user: User = Depends(get_user),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin])),
        db_session: AsyncSession = Depends(get_session),
):
    user = await UserRepo.delete(
        user=user,
        db_session=db_session
    )
    return DataResponse(
        data={
            'user': UserOutAdminScheme.model_validate(user)
        }
    )
