import time
import uuid

from fastapi import Response, Request

import jwt

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, ConfirmationType
from src.database.repos.confirmation_code import ConfirmationCodeRepo
from src.logger import get_logger
from src.settings import (
    AppConfig,
    JWTConfig,
    LOGGER_PREFIX,
    KafkaConfig,
    UnisenderConfig,
    FrontConfig,
)
from src.util.auth.schemes import UserInfo, RefreshPayload, TokensScheme
from src.util.brokers.producer.kafka import KafkaProducer
from src.util.mail.schemes import SendEmailScheme
from src.util.storage.classes import RedisHandler

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
logger = get_logger(LOGGER_PREFIX + __name__)
app_config = AppConfig()
jwt_config = JWTConfig()
unisender_config = UnisenderConfig()
front_config = FrontConfig()


def get_password_hash(password: str) -> str:
    password = f'{password}'
    return pwd_context.hash(password, salt=app_config.secret_key)


def get_payload(
    dict_payload: dict, is_access: bool
) -> UserInfo | RefreshPayload:
    scheme = UserInfo if is_access else RefreshPayload
    try:
        return scheme(**dict_payload.get(jwt_config.user_info_property))
    except Exception as e:
        logger.exception(e)


def verify_jwt(
    token: str, is_access: bool = True
) -> UserInfo | RefreshPayload | None:
    try:
        payload = jwt.decode(
            token, jwt_config.secret_key, algorithms=[jwt_config.algorithm]
        )
        return get_payload(payload, is_access)
    except (
        jwt.exceptions.DecodeError,
        jwt.exceptions.ExpiredSignatureError,
    ) as e:
        logger.error('Got jwt decode error: %s', e)
        return None
    except Exception as e:
        logger.exception(e)
        raise


async def put_tokens_in_black_list(token_ids: list[uuid.UUID]) -> None:
    await RedisHandler().set_batch(
        key='token',
        values=[str(t) for t in token_ids],
        ex=jwt_config.refresh_jwt_exp_sec,
    )


def get_user_agent(request: Request) -> str:
    user_agent = request.headers.get('user-agent')
    return user_agent[:100] if user_agent else 'not provided'


def get_authenticated_response(response: Response, tokens: TokensScheme):
    # response = JSONResponse({'detail': 'Аутентифицирован'})
    response.set_cookie(
        jwt_config.auth_cookie_name,
        tokens.access_token,
        int(time.time()) + jwt_config.auth_jwt_exp_sec,
    )
    response.set_cookie(
        jwt_config.refresh_cookie_name,
        tokens.refresh_token,
        int(time.time()) + jwt_config.refresh_jwt_exp_sec,
    )
    return response


async def send_email_confirmation_message(
    user: User, email: str, db_session: AsyncSession
) -> None:
    producer = KafkaProducer(
        bootstrap_servers=KafkaConfig.address, topic=KafkaConfig.mail_topic
    )
    confirmation_code = await ConfirmationCodeRepo.create(
        user_id=user.id,
        reason=ConfirmationType.registration,
        db_session=db_session,
    )
    kafka_message = SendEmailScheme(
        to_address=email,
        from_address=unisender_config.from_address,
        from_name=unisender_config.from_name,
        subject=unisender_config.email_confirmation_subject,
        template_id=unisender_config.email_confirmation_template_id,
        params={
            'link': f'{front_config.address}'
            f'{front_config.confirm_email_endpoint}'
            f'?code={confirmation_code.code}'
        },
    )
    await producer.send_message(kafka_message.model_dump(mode='json'))


async def close_sessions(user_id: uuid.UUID):
    # TODO: implement
    pass

