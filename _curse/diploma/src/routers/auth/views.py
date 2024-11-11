import json
import time

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status
)

from pydantic import EmailStr
from starlette.responses import JSONResponse

from src.database.models import ConfirmationType
from src.depends import get_session
from src.http_responses import get_responses
from src.responses import BaseResponse
from src.routers.auth.schemes import RegistrationScheme, ResetPasswordScheme
from src.routers.users.schemes import CreateUserScheme
from src.database.repos.confirmation_code import ConfirmationCodeRepo
from src.database.repos.session import SessionRepo
from src.database.repos.user import UserRepo
from src.settings import Role, KafkaConfig, UnisenderConfig, JWTConfig
from src.util.auth.classes import AuthHandler
from src.util.auth.helpers import get_password_hash, get_user_agent
from src.util.auth.schemes import LoginScheme

from sqlalchemy.ext.asyncio import AsyncSession

from src.util.brokers.producer.kafka import KafkaProducer
from src.util.mail.schemes import SendEmailScheme

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post(
    '/login/',
    # response_model=BaseResponse,
    responses=get_responses(404)
)
async def login(
        login_data: LoginScheme,
        request: Request,
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepo.get_by_email(
        email=login_data.email,
        db_session=db_session
    )
    print('USER', user)
    print(login_data, user.password_hash, get_password_hash(login_data.password), user.password_hash == get_password_hash(login_data.password))
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
    await SessionRepo.close_all(
        user_id=user.id,
        ip=request.client.host,
        user_agent=get_user_agent(request),
        db_session=db_session
    )
    await db_session.refresh(user)
    tokens = await AuthHandler.login(
        user=user,
        request=request,
        db_session=db_session
    )
    response = JSONResponse(json.dumps({'detail': 'Аутентифицирован'}))
    response.set_cookie(
        JWTConfig.auth_cookie_name,
        tokens.access_token,
        int(time.time()) + JWTConfig.auth_jwt_exp_sec,
    )
    response.set_cookie(
        JWTConfig.refresh_cookie_name,
        tokens.refresh_token,
        int(time.time()) + JWTConfig.refresh_jwt_exp_sec,
    )
    return response


@router.post(
    '/register/',
    response_model=BaseResponse,
    responses=get_responses(409)
)
async def register(
        registration_data: RegistrationScheme,
        db_session: AsyncSession = Depends(get_session)
):
    if await UserRepo.name_is_taken(
        name=registration_data.name,
        db_session=db_session
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Имя занято'
        )
    user = await UserRepo.create(
        user_data=CreateUserScheme(
            name=registration_data.name,
            email=registration_data.email,
            email_verified=False,
            password=registration_data.password,
            role=Role.user
        ),
        db_session=db_session
    )
    producer = KafkaProducer(
        bootstrap_servers=KafkaConfig.address,
        topic=KafkaConfig.mail_topic
    )
    confirmation_code = await ConfirmationCodeRepo.create(
        user_id=user.id,
        reason=ConfirmationType.registration,
        db_session=db_session
    )
    kafka_message = SendEmailScheme(
        to_address=registration_data.email,
        from_address=UnisenderConfig.from_address,
        from_name=UnisenderConfig.from_name,
        subject=UnisenderConfig.email_confirmation_subject,
        template_id=UnisenderConfig.email_confirmation_template_id,
        params={
            'code': confirmation_code.code
        }
    )
    await producer.send_message(kafka_message.model_dump(mode='json'))
    return BaseResponse(message='Регистрация успешна. Проверьте почту')


@router.post(
    '/registration/confirm/',
    response_model=BaseResponse,
    responses=get_responses(400, 404)
)
async def confirm_email(
        code: str,
        db_session: AsyncSession = Depends(get_session)
):
    confirmation_code = await ConfirmationCodeRepo.get(
        value=code,
        reason=ConfirmationType.registration,
        db_session=db_session
    )
    if not confirmation_code or confirmation_code.code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неправильный код'
        )

    user = await UserRepo.get_by_id(
        user_id=confirmation_code.user_id,
        db_session=db_session
    )
    if not user or user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден'
        )
    user.email_verified = True
    db_session.add(user)
    await db_session.commit()
    return BaseResponse(message='Почта подтверждена. Можно входить')


@router.post(
    '/restore-password/request/',
    response_model=BaseResponse,
    responses=get_responses(404)
)
async def request_password_restoration_code(
        email: EmailStr,
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepo.get_by_email(
        email=email,
        db_session=db_session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Неправильный адрес электронной почты'
        )
    confirmation_code = await ConfirmationCodeRepo.create(
        user_id=user.id,
        reason=ConfirmationType.password_reset,
        db_session=db_session
    )
    producer = KafkaProducer(
        bootstrap_servers=KafkaConfig.address,
        topic=KafkaConfig.mail_topic
    )
    kafka_message = SendEmailScheme(
        to_address=email,
        from_address=UnisenderConfig.from_address,
        from_name=UnisenderConfig.from_name,
        subject=UnisenderConfig.password_recovery_subject,
        template_id=UnisenderConfig.password_recovery_template_id,
        params={
            'code': confirmation_code.code
        }
    )
    await producer.send_message(kafka_message.model_dump(mode='json'))
    return BaseResponse(message='Сообщение отправляется на почту')


@router.patch(
    '/restore-password/confirm/',
    response_model=BaseResponse,
    responses=get_responses(400, 404)
)
async def restore_password(
        request_data: ResetPasswordScheme,
        db_session: AsyncSession = Depends(get_session)
):
    confirmation_code = await ConfirmationCodeRepo.get(
        value=request_data.code,
        reason=ConfirmationType.password_reset,
        db_session=db_session
    )
    if not confirmation_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Код восстановления пароля не найден'
        )
    new_password_hash = get_password_hash(request_data.new_password)
    await UserRepo.update_password_hash(
        user_id=confirmation_code.user_id,
        new_password_hash=new_password_hash,
        db_session=db_session
    )
    return BaseResponse(message='Пароль успешно изменён')


@router.post(
    '/refresh/',
    response_model=BaseResponse,
    responses=get_responses(400, 401)
)
async def refresh_tokens(
        refresh_token: str,
        request: Request,
        response: Response,
        db_session: AsyncSession = Depends(get_session)
):
    tokens = await AuthHandler.refresh_tokens(
        refresh_token=refresh_token,
        request=request,
        db_session=db_session
    )
    response.set_cookie(
        JWTConfig.auth_cookie_name,
        tokens.access_token,
        int(time.time()) + JWTConfig.auth_jwt_exp_sec
    )
    response.set_cookie(
        JWTConfig.refresh_cookie_name,
        tokens.refresh_token,
        int(time.time()) + JWTConfig.refresh_jwt_exp_sec
    )
    return BaseResponse(message='Токены обновлены')


@router.get(
    '/logout/',
    response_model=BaseResponse
)
async def logout(
        response: Response
):
    response.set_cookie(JWTConfig.auth_cookie_name, '')
    response.set_cookie(JWTConfig.refresh_cookie_name, '')
    return BaseResponse(message='Вышел')
