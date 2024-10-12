import enum

from dotenv import load_dotenv

from src.util.common.classes import EnvParameter 


load_dotenv()

class AppConfig:
    app_name = EnvParameter('APP_NAME', default='GPTranslate')
    # secret_key = EnvParameter('APP_SECRET_KEY')
    secret_key = '123456789012345678901e'
    conf_code_exp_seconds = 60 * 15


class Database:
    prefix = EnvParameter('DATABASE_PREFIX', default='gptranslate_')
    url = EnvParameter('DATABASE_URL')
    pool_size = EnvParameter(
        'DB_POOL_SIZE', type_=int, default=5
    )
    max_overflow = EnvParameter(
        'DB_MAX_OVERFLOW', type_=int, default=50
    )
    pool_recycle = EnvParameter(
        'DB_POOL_RECYCLE', type_=int, default=600
    )
    pool_pre_ping = EnvParameter(
        'DB_POOL_PRE_PING', type_=bool, default='false'
    )


class JWTConfig:
    secret_key = EnvParameter(
        'JWT_SECRET_KEY',
        default=(
            '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
        )
    )
    algorithm = 'HS256'
    auth_jwt_exp_sec = EnvParameter(
        'JWT_AUTH_EXP', type_=int, default=60 * 60
    )
    refresh_jwt_exp_sec = EnvParameter(
        'JWT_REFRESH_EXP', type_=int, default=60 * 60 * 24 * 30
    )
    user_info_property = 'user_info'


class Role(enum.StrEnum):
    user = 'Пользователь'
    moderator = 'Модератор'
    admin = 'Администратор'
