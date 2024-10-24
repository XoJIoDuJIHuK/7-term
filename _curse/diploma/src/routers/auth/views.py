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
from src.services.session import SessionRepository
from src.services.user import UserRepository
from src.settings import Role, KafkaConfig, UnisenderConfig
from src.util.auth.classes import AuthHandler
from src.util.auth.helpers import get_password_hash, get_user_agent
from src.util.auth.schemes import LoginScheme, TokensScheme

from sqlalchemy.ext.asyncio import AsyncSession

from src.util.brokers.producer.kafka import KafkaProducer
from src.util.mail.schemes import SendEmailScheme

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


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
    await SessionRepository.close_all(
        user_id=user.id,
        ip=request.client.host,
        user_agent=get_user_agent(request),
        db_session=db_session
    )
    return await AuthHandler.login(
        user=user,
        request=request,
        db_session=db_session
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
    producer = KafkaProducer(
        bootstrap_servers=KafkaConfig.address,
        topic=KafkaConfig.mail_topic
    )
    confirmation_code = await ConfirmationCodeRepository.create(
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
        email: EmailStr,
        db_session: AsyncSession = Depends(get_session)
):
    user = await UserRepository.get_by_email(
        email=email,
        db_session=db_session
    )
    if not user or user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь не найден'
        )
    confirmation_code = await ConfirmationCodeRepository.get(
        value=code,
        reason=ConfirmationType.registration,
        db_session=db_session
    )
    if not confirmation_code or confirmation_code.code != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Неправильный код'
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
    user = await UserRepository.get_by_email(
        email=email,
        db_session=db_session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Неправильный адрес электронной почты'
        )
    confirmation_code = await ConfirmationCodeRepository.create(
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
