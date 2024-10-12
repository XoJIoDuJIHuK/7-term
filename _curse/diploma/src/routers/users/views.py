import uuid

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Path,
    status,
)

from fastapi_pagination import Params

from src.database import get_session
from src.database.models import User
from src.routers.users.helpers import get_user
from src.routers.users.schemes import (
    CreateUserScheme,
    FilterUserScheme,
    UserOutAdminScheme,
    UserOutScheme, EditUserScheme,
)
from src.services.user import UserRepository
from src.settings import Role
from src.util.auth.classes import JWTBearer
from src.util.auth.schemes import UserInfo

from sqlalchemy.ext.asyncio import AsyncSession

from src.util.common.schemes import SuccessResponse
from src.util.time.helpers import get_utc_now

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get(
    '/me/'
)
async def get_my_info(
        user_info: UserInfo = Depends(JWTBearer()),
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepository.get_by_id(
        user_id=user_info.id,
        db_session=db_session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь не найден'
        )
    return UserOutScheme(
        name=user.name,
        email=user.email,
        role=user.role
    )


@router.get(
    '/'
)
async def get_list(
        filters: FilterUserScheme,
        pagination_params: Params = Depends(),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.admin])),
        db_session: AsyncSession = Depends(get_session),
):
    page = await UserRepository.get_list(
        pagination_params=pagination_params,
        filter_params=filters,
        db_session=db_session
    )
    page.items = [UserOutAdminScheme.model_validate(u) for u in page.items]
    return page


@router.patch(
    '/name/'
)
async def change_name(
        new_name: str = Form(min_length=1, max_length=20),
        user_info: UserInfo = Depends(JWTBearer()),
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepository.get_by_id(
        user_id=user_info.id,
        db_session=db_session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь не найден'
        )
    if user.name == new_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Новое имя не должно совпадать со старым'
        )
    user.name = new_name
    db_session.add(user)
    await db_session.commit()
    return SuccessResponse(message='Имя успешно изменено')


@router.post(
    '/'
)
async def create_user(
        new_user_data: CreateUserScheme,
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.admin])),
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepository.create(
        user_data=new_user_data,
        db_session=db_session
    )
    return UserOutAdminScheme.model_validate(user)


@router.put(
    '/{user_id}/'
)
async def update_user(
        new_user_info: EditUserScheme,
        user: User = Depends(get_user),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.admin])),
        db_session: AsyncSession = Depends(get_session),
):
    # TODO: implement
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return UserOutAdminScheme.model_validate(user)


@router.delete(
    '/{user_id}/'
)
async def delete_user(
        user: User = Depends(get_user),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.admin])),
        db_session: AsyncSession = Depends(get_session),
):
    user.deleted_at = get_utc_now()
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return UserOutAdminScheme.model_validate(user)
