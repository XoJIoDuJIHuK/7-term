import enum
from pathlib import Path

from dotenv import load_dotenv

from src.util.common.classes import EnvParameter

load_dotenv()

LOGGER_PREFIX = 'diploma_'
BASE_DIR = Path(__file__).resolve().parent.resolve().parent

class AppConfig:
    app_name = EnvParameter('APP_NAME', default='GPTranslate')
    # secret_key = EnvParameter('APP_SECRET_KEY')
    secret_key = '123456789012345678901e'
    conf_code_exp_seconds = 60 * 15
    debug = EnvParameter('APP_DEBUG', default=True)
    websocket_timeout_sec = 5


class Database:
    prefix = EnvParameter('DATABASE_PREFIX', default='gptranslate_')
    url = EnvParameter(
        'DATABASE_URL',
        default='postgresql+asyncpg://admin:admin@127.0.0.1:5432/diploma'
    )
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
        'JWT_AUTH_EXP', type_=int, default=60 * 60 * 1000
    )
    auth_cookie_name = 'access_token'
    refresh_jwt_exp_sec = EnvParameter(
        'JWT_REFRESH_EXP', type_=int, default=60 * 60 * 24 * 30
    )
    refresh_cookie_name = 'refresh_token'
    user_info_property = 'user_info'


class Role(enum.StrEnum):
    user = 'Пользователь'
    moderator = 'Модератор'
    admin = 'Администратор'


class AppEvent(enum.Enum):
    translation_start = 1
    translation_end = 2


class TextTranslationConfig:
    max_words_in_text = EnvParameter(
        'TRANSLATOR_MAX_WORDS_IN_TEXT',
        type_=int,
        default=10000,
    )
    max_words_in_chunk = EnvParameter(
        'TRANSLATOR_MAX_WORDS_IN_CHUNK',
        type_=int,
        default=200,
    )
    special_characters = ['\\n', '\\t']


class G4FConfig:
    address = EnvParameter('G4F_ADDRESS', default='http://g4f:1337')


class GeminiConfig:
    api_key = EnvParameter('GEMINI_API_KEY')
    gemini_project_id = EnvParameter('GEMINI_PROJECT_ID')


class KafkaConfig:
    translation_topic = EnvParameter('TRANSLATION_KAFKA_TOPIC')
    mail_topic = EnvParameter('MAIL_KAFKA_TOPIC')
    address = EnvParameter('KAFKA_ADDRESS')
    group_id = EnvParameter('KAFKA_GROUP_ID')


class RedisConfig:
    host = EnvParameter('REDIS_HOST', default='redis')
    port = EnvParameter('REDIS_PORT', type_=int, default=6379)
    db = EnvParameter('REDIS_DB', default=0)


class TranslationTaskConfig:
    MAX_RETRIES = EnvParameter(
        'TRANSLATION_TASK_MAX_RETRIES', type_=int, default=5
    )
    RESEND_MESSAGE_MAX_RETRIES = EnvParameter(
        'RESEND_MESSAGE_MAX_RETRIES', type_=int, default=25
    )


class UnisenderConfig:
    from_address = EnvParameter('UNISENDER_FROM_ADDRESS')
    from_name = EnvParameter('UNISENDER_FROM_NAME')
    api_key = EnvParameter('UNISENDER_API_KEY')
    email_confirmation_subject = EnvParameter(
        'UNISENDER_EMAIL_CONFIRMATION_SUBJECT'
    )
    password_recovery_subject = EnvParameter(
        'UNISENDER_PASSWORD_RECOVERY_SUBJECT'
    )
    email_confirmation_template_id = EnvParameter(
        'UNISENDER_EMAIL_CONFIRMATION_TEMPLATE_ID'
    )
    password_recovery_template_id = EnvParameter(
        'UNISENDER_PASSWORD_RECOVERY_TEMPLATE_ID'
    )
    translation_complete_template_id = EnvParameter(
        'UNISENDER_TRANSLATION_COMPLETE_TEMPLATE_ID'
    )
    api_url = EnvParameter('UNISENDER_API_URL')
    list_id = EnvParameter('UNISENDER_LIST_ID')


class NotificationConfig:
    class Subjects:
        new_message = 'Непрочитанное сообщение'
        translation_ended = 'Перевод завершён'
        translation_error = 'Ошибка при переводе'
    time_to_live_in_redis = 10
    topic_name = 'notifications_{}'
    translation_success_message = (
        'Статья {article_name} успешно переведена на {target_lang} язык'
    )
