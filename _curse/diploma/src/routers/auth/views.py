from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status
)
from sqlalchemy.testing.config import db_url

from src.database import get_session
from src.routers.auth.schemes import RegistrationScheme
from src.routers.users.schemes import CreateUserScheme
from src.services.user import UserRepository
from src.settings import Role
from src.util.auth.classes import AuthHandler, JWTBearer
from src.util.auth.helpers import get_password_hash
from src.util.auth.schemes import LoginScheme, TokensScheme, UserInfo
from src.util.common.schemes import SuccessResponse

from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post('/register/', response_model=None)
async def register(
        registration_data: RegistrationScheme,
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepository.create(
        user_data=CreateUserScheme(
            name=registration_data.name,
            email=registration_data.email,
            password_hash=get_password_hash(registration_data.password),
            role=Role.user
        ),
        db_session=db_session
    )
    return SuccessResponse(message='Регистрация успешна')


@router.post(
    '/login/',
    responses={
        200: {
            'model': TokensScheme
        },
        404: {
            'model': None
        }
    }
)
async def login(
        login_data: LoginScheme,
        request: Request,
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepository.get_by_email(
        email=login_data.email,
        db_session=db_session
    )
    if (
            not user or
            user.password_hash != get_password_hash(login_data.password)
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Неправильные данные для входа'
        )
    return await AuthHandler.login(
        user=user,
        request=request,
        db_session=db_session
    )


@router.patch(
    '/password/',
    responses={

    }
)
async def restore_password(
        new_password: str,
        user_info: UserInfo = Depends(JWTBearer),
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepository.get_by_id(
        user_id=user_info.id,
        db_session=db_session
    )
    new_password_hash = get_password_hash(new_password)
    if new_password_hash == user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пароли не могут совпадать'
        )
    user.password_hash = new_password_hash
    db_session.add(user)
    await db_session.commit()
    return SuccessResponse(message='Пароль успешно изменён')
