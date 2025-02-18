import datetime
import enum
import uuid

from src.database import Base

from src.util.time.helpers import (
    get_utc_now,
)

from src.settings import Database, Role

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UUID,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


database_config = Database()


class ReportStatus(enum.StrEnum):
    open = 'Открыта'
    closed = 'Закрыта пользователем'
    rejected = 'Отклонена'
    satisfied = 'Удовлетворена'
    # TODO: add refund


class TranslationTaskStatus(enum.StrEnum):
    created = 'Создана'
    started = 'Запущена'
    failed = 'Ошибка'
    completed = 'Завершена'


class NotificationType(enum.StrEnum):
    info = 'info'
    success = 'success'
    warning = 'warning'
    error = 'error'


class ConfirmationType(enum.StrEnum):
    registration = 'registration'
    password_reset = 'password_reset'


class User(Base):
    __tablename__ = f'{database_config.prefix}users'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String, unique=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str] = mapped_column(String(60))
    role: Mapped[Role] = mapped_column(
        Enum(Role, name='user_role'), default=Role.user
    )
    logged_with_provider: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment='External OAuth provider name user has registered with',
    )
    provider_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment="User's ID from OAuth provider user has registered with",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )


class Session(Base):
    __tablename__ = f'{database_config.prefix}sessions'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{database_config.prefix}users.id', ondelete='CASCADE')
    )
    ip: Mapped[str] = mapped_column(String(15))
    user_agent: Mapped[str] = mapped_column(String(100))
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now
    )
    closed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )


class ConfirmationCode(Base):
    __tablename__ = f'{database_config.prefix}confirmation_codes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(
        String, unique=True, comment='The value of the code'
    )
    reason: Mapped[ConfirmationType] = mapped_column(
        Enum(ConfirmationType), default=ConfirmationType.registration
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    expired_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now
    )


class Language(Base):
    __tablename__ = f'{database_config.prefix}languages'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    iso_code: Mapped[str] = mapped_column(String, unique=True)


class Article(Base):
    __tablename__ = f'{database_config.prefix}articles'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(50))
    text: Mapped[str] = mapped_column(Text)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    language_id: Mapped[int | None] = mapped_column(
        ForeignKey(f'{Language.__tablename__}.id', ondelete='CASCADE'),
        nullable=True,
    )
    original_article_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(f'{database_config.prefix}articles.id', ondelete='CASCADE'),
        nullable=True,
    )
    like: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    report: Mapped['Report'] = relationship(
        'Report',
        back_populates='article',
        cascade='all, delete-orphan',
        uselist=False,
        lazy='joined',
    )
    language: Mapped[Language] = relationship(
        'Language', uselist=False, lazy='joined'
    )
    original_article: Mapped['Article'] = relationship(
        'Article', uselist=False, lazy='joined'
    )


class ReportReason(Base):
    __tablename__ = f'{database_config.prefix}report_reasons'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, unique=True)
    order_position: Mapped[int] = mapped_column(Integer, unique=True)


class Report(Base):
    __tablename__ = f'{database_config.prefix}reports'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    text: Mapped[str] = mapped_column(String(1024))
    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Article.__tablename__}.id', ondelete='CASCADE')
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus), default=ReportStatus.open
    )
    closed_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE'),
        nullable=True,
    )
    reason_id: Mapped[int] = mapped_column(
        ForeignKey(f'{ReportReason.__tablename__}.id', ondelete='CASCADE')
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now
    )
    closed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    article: Mapped[Article] = relationship(
        'Article',
        back_populates='report',
        uselist=False,
        lazy='joined',
    )
    closed_by_user: Mapped[User] = relationship(
        'User',
        uselist=False,
        lazy='joined',
    )
    reason: Mapped[ReportReason] = relationship(
        'ReportReason',
        uselist=False,
        lazy='joined',
    )


class Comment(Base):
    __tablename__ = f'{database_config.prefix}report_comments'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    text: Mapped[str] = mapped_column(String(100))
    sender_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Report.__tablename__}.id', ondelete='CASCADE')
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now
    )


class StylePrompt(Base):
    __tablename__ = f'{database_config.prefix}style_prompts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(20), unique=True)
    text: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )


class AIModel(Base):
    __tablename__ = f'{database_config.prefix}ai_models'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    show_name: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now, nullable=False
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )


class TranslationConfig(Base):
    __tablename__ = f'{database_config.prefix}configs'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    prompt_id: Mapped[int | None] = mapped_column(
        ForeignKey(f'{StylePrompt.__tablename__}.id', ondelete='CASCADE'),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        String(20),
    )
    language_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    model_id: Mapped[int | None] = mapped_column(
        ForeignKey(f'{AIModel.__tablename__}.id', ondelete='CASCADE'),
        nullable=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )


class TranslationTask(Base):
    __tablename__ = f'{database_config.prefix}translation_tasks'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Article.__tablename__}.id', ondelete='CASCADE')
    )
    target_language_id: Mapped[int] = mapped_column(
        ForeignKey(f'{Language.__tablename__}.id', ondelete='CASCADE')
    )
    prompt_id: Mapped[int] = mapped_column(
        ForeignKey(f'{StylePrompt.__tablename__}.id', ondelete='CASCADE')
    )
    model_id: Mapped[int] = mapped_column(
        ForeignKey(f'{AIModel.__tablename__}.id', ondelete='CASCADE')
    )
    status: Mapped[TranslationTaskStatus] = mapped_column(
        Enum(TranslationTaskStatus), default=TranslationTaskStatus.created
    )
    data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=True,
        comment='Additional data related to the translation task '
        '(e.g., errors or metadata)',
    )
    translated_article_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(f'{Article.__tablename__}.id', ondelete='CASCADE'),
        nullable=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )


class Notification(Base):
    __tablename__ = f'{database_config.prefix}notifications'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(String)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType))
    read_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=get_utc_now
    )
