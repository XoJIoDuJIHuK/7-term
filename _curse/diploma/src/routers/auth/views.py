from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Query,
    status
)

from pydantic import EmailStr

from src.database.models import ConfirmationType
from src.depends import get_session
from src.http_responses import get_responses
from src.responses import BaseResponse, DataResponse
from src.routers.auth.schemes import RegistrationScheme
from src.routers.users.schemes import CreateUserScheme
from src.services.confirmation_code import ConfirmationCodeRepository
from src.services.user import UserRepository
from src.settings import Role
from src.util.auth.classes import AuthHandler
from src.util.auth.helpers import get_password_hash
from src.util.auth.schemes import LoginScheme, TokensScheme

from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post(
    '/register/',
    response_model=BaseResponse,
    responses=get_responses(409)
)
async def register(
        registration_data: RegistrationScheme,
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepository.create(
        user_data=CreateUserScheme(
            name=registration_data.name,
            email=registration_data.email,
            email_verified=False,
            password=registration_data.password,
            role=Role.user
        ),
        db_session=db_session
    )
    return BaseResponse(message='Регистрация успешна')


@router.post(
    '/login/',
    response_model=DataResponse.single_by_key(
        'tokens',
        TokensScheme
    ),
    responses=get_responses(404)
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
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Подтвердите адрес электронной почты'
        )
    return await AuthHandler.login(
        user=user,
        request=request,
        db_session=db_session
    )


@router.post(
    '/restore-password/request/',
    response_model=BaseResponse,
    responses=get_responses(404)
)
async def request_password_restoration_code(
        email: EmailStr,
        db_session: AsyncSession
):



@router.patch(
    '/restore-password/confirm/',
    response_model=BaseResponse,
    responses=get_responses(400, 404)
)
async def restore_password(
        new_password: str,
        code: str,
        db_session: AsyncSession = Depends(get_session)
):
    confirmation_code = await ConfirmationCodeRepository.get(
        value=code,
        reason=ConfirmationType.password_reset,
        db_session=db_session
    )
    if not confirmation_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Код восстановления пароля не найден'
        )
    new_password_hash = get_password_hash(new_password)
    # TODO: move to service
    await UserRepository.update_password_hash(
        user_id=confirmation_code.user_id,
        new_password_hash=new_password_hash,
        db_session=db_session
    )
    return BaseResponse(message='Пароль успешно изменён')


@router.post(
    '/refresh/',
    response_model=DataResponse.single_by_key(
        'tokens',
        TokensScheme
    ),
    responses=get_responses(400, 401)
)
async def refresh_tokens(
        refresh_token: str,
        request: Request,
        db_session: AsyncSession = Depends(get_session)
):
    return await AuthHandler.refresh_tokens(
        refresh_token=refresh_token,
        request=request,
        db_session=db_session
    )
