import time
import uuid

from fastapi import HTTPException, Request, status

import jwt

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from src.database.models import User, ConfirmationType
from src.database.repos.confirmation_code import ConfirmationCodeRepo
from src.logger import get_logger
from src.settings import AppConfig, JWTConfig, LOGGER_PREFIX, KafkaConfig, \
    UnisenderConfig, FrontConfig
from src.util.auth.schemes import UserInfo, RefreshPayload, TokensScheme
from src.util.brokers.producer.kafka import KafkaProducer
from src.util.mail.schemes import SendEmailScheme
from src.util.storage.classes import RedisHandler

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
logger = get_logger(LOGGER_PREFIX + __name__)


def get_password_hash(password: str) -> str:
    password = f'{password}'
    return pwd_context.hash(password, salt=AppConfig.secret_key)


def get_payload(
        dict_payload: dict,
        is_access: bool
) -> UserInfo | RefreshPayload:
    scheme = UserInfo if is_access else RefreshPayload
    try:
        return scheme(**dict_payload.get(JWTConfig.user_info_property))
    except Exception as e:
        logger.exception(e)


def verify_jwt(
        token: str,
        is_access: bool = True
) -> UserInfo | RefreshPayload | None:
    try:
        payload = jwt.decode(
            token, JWTConfig.secret_key, algorithms=[JWTConfig.algorithm]
        )
        logger.info(f'JWT payload: {payload}')
        return get_payload(payload, is_access)
    except (
        jwt.exceptions.DecodeError,
        jwt.exceptions.ExpiredSignatureError
    ) as e:
        logger.error('Got jwt decode error: %s', e)
        return None
    except Exception as e:
        logger.exception(e)
        raise


def put_tokens_in_black_list(
        token_ids: list[uuid.UUID]
) -> None:
    RedisHandler().set_batch(
        key='token',
        values=[str(t) for t in token_ids],
        ex=JWTConfig.refresh_jwt_exp_sec
    )


def get_user_agent(request: Request) -> str:
    user_agent = request.headers.get('user-agent')
    return user_agent[:100] if user_agent else 'not provided'


def get_authenticated_response(
        tokens: TokensScheme
):
    response = JSONResponse({'detail': 'Аутентифицирован'})
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


async def send_email_confirmation_message(
        user: User,
        email: str,
        db_session: AsyncSession
) -> None:
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
        to_address=email,
        from_address=UnisenderConfig.from_address,
        from_name=UnisenderConfig.from_name,
        subject=UnisenderConfig.email_confirmation_subject,
        template_id=UnisenderConfig.email_confirmation_template_id,
        params={
            'link': f'{FrontConfig.address}'
                    f'{FrontConfig.confirm_email_endpoint}'
                    f'?code={confirmation_code.code}'
        }
    )
    await producer.send_message(kafka_message.model_dump(mode='json'))


async def close_sessions(
        user_id: uuid.UUID
):
    # TODO: implement
    pass