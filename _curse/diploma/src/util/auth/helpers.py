import logging
import uuid

from fastapi import HTTPException, Request, status

from jose import JWTError, jwt

from passlib.context import CryptContext

from src.settings import AppConfig, JWTConfig, LOGGER_PREFIX
from src.util.auth.schemes import UserInfo, RefreshPayload
from src.util.storage.classes import RedisHandler

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
logger = logging.getLogger(LOGGER_PREFIX + __name__)


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
) -> UserInfo | RefreshPayload:
    try:
        payload = jwt.decode(
            token, JWTConfig.secret_key, algorithms=[JWTConfig.algorithm]
        )
        return get_payload(payload, is_access)
    except JWTError as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неправильный токен'
        )


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


async def close_sessions(
        user_id: uuid.UUID
):
    pass