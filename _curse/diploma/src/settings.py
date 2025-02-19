import dataclasses
import enum
from abc import ABCMeta
from pathlib import Path
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.util.common.classes import EnvParameter

LOGGER_PREFIX = 'diploma_'
BASE_DIR = Path(__file__).resolve().parent.resolve().parent


def settings_class(env_prefix: str):
    def wrapper(class_obj):
        class_obj.model_config = SettingsConfigDict(
            env_prefix=env_prefix, validate_default=False, extra='ignore'
        )
        return class_obj

    return wrapper


@settings_class('APP_CONFIG_')
class AppConfig(BaseSettings):
    app_name: str = 'GPTranslate'
    secret_key: str = '123456789012345678901e'
    conf_code_exp_seconds: int = 60 * 15
    debug: bool = False
    websocket_timeout_sec: int = 5
    close_sessions_on_same_device_login: bool = True


@settings_class('DATABASE_')
class Database(BaseSettings):
    prefix: str = ''
    url: str
    pool_size: int = 5
    pool_recycle: int = 600
    pool_pre_ping: bool = False


@settings_class('JWT_CONFIG_')
class JWTConfig(BaseSettings):
    secret_key: str = (
        '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
    )
    algorithm: str = 'HS256'
    auth_jwt_exp_sec: int = 10
    auth_cookie_name: str = 'access_token'
    refresh_jwt_exp_sec: int = 60 * 60 * 24 * 30
    refresh_cookie_name: str = 'refresh_token'
    user_info_property: str = 'user_info'


class Role(enum.StrEnum):
    user = 'Пользователь'
    moderator = 'Модератор'
    admin = 'Администратор'


class AppEvent(enum.Enum):
    translation_start = 1
    translation_end = 2


@settings_class('TEXT_TRANSLATION_')
class TextTranslationConfig(BaseSettings):
    max_text_length: int = 10000000
    max_words_in_text: int = 1000000
    max_words_in_chunk: int = 400
    special_characters: ClassVar = ['\\n', '\\t']


@settings_class('G4F_')
class G4FConfig(BaseSettings):
    address: str = 'http://g4f:1337/'


class KafkaConfig:
    translation_topic: str
    mail_topic: str
    address: str
    group_id: str
    max_poll_interval_ms: int = 30000


@settings_class('OPENROUTER_')
class OpenRouterConfig(BaseSettings):
    api_key: str


@settings_class('RABBIT_')
class RabbitMQConfig(BaseSettings):
    host: str
    login: str
    password: str
    translation_topic: str
    mail_topic: str


@settings_class('REDIS_CONFIG_')
class RedisConfig(BaseSettings):
    host: str = 'redis'
    port: int = 6379
    db: int = 0


@settings_class('TRANSLATION_TASK_')
class TranslationTaskConfig(BaseSettings):
    MAX_RETRIES: int = 5
    RESEND_MESSAGE_MAX_RETRIES: int = 5


@settings_class('UNISENDER_')
class UnisenderConfig(BaseSettings):
    from_address: str
    from_name: str
    api_key: str
    email_confirmation_subject: str
    password_recovery_subject: str
    translation_complete_subject: str
    email_confirmation_template_id: str
    password_recovery_template_id: str
    translation_complete_template_id: str
    api_url: str
    list_id: str


@settings_class('FRONT_')
class FrontConfig(BaseSettings):
    address: str
    change_password_endpoint: str
    confirm_email_endpoint: str


@settings_class('NOTIFICATION_CONFIG_')
class NotificationConfig(BaseSettings):
    class Subjects:
        new_message = 'Непрочитанное сообщение'
        translation_ended = 'Перевод завершён'
        translation_error = 'Ошибка при переводе'

    time_to_live_in_redis: int = 10
    topic_name: str = 'notifications_{}'
    translation_success_message: str = (
        'Статья {article_name} успешно переведена на {target_lang} язык'
    )


@settings_class('GOOGLE_')
class GoogleOauth2Config(BaseSettings):
    response_type: str = 'code'
    CLIENT_ID: str
    CLIENT_SECRET: str
    AUTHORIZATION_URL: str = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URL: str = 'https://oauth2.googleapis.com/token'
    VALIDATE_URL: str = 'https://openidconnect.googleapis.com/v1/userinfo'
    REDIRECT_URI: str = 'http://localhost:8000/oauth/google/callback'
    SCOPE: str = 'email'


class OAuthProvider(enum.StrEnum):
    google = 'google'


providers = {
    OAuthProvider.google.value: GoogleOauth2Config(),
}


@settings_class('OAUTH_CONFIG_')
class OAuthConfig(BaseSettings):
    code_expiration_time: int = 60 * 10
    auth_token_expiration_time: int = 60 * 60
    refresh_token_time_expiration: int = 60 * 60 * 24 * 7
    algorithm: str = 'HS256'
    secret_key: str = (
        '1164znbm8jjmb3l9aqe0wz8t45ni30h3vev65p02pannvv1xwku9v74g98spw4us'
    )
    session_data_property: str = 'oauth_login_data'
