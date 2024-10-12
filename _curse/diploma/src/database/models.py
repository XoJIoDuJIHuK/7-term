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
    UUID,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


class ReportStatus(enum.StrEnum):
    open = 'Открыт'
    closed = 'Закрыт пользователем'
    rejected = 'Отклонён'
    # TODO: add refund


class TranslationTaskStatus(enum.StrEnum):
    started = 'Запущена'
    failed = 'Ошибка'
    completed = 'Завершена'


class NotificationType(enum.Enum):
    info = 1
    warning = 2
    error = 3


class User(Base):
    __tablename__ = f'{Database.prefix}users'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(20),
        unique=True
    )
    email: Mapped[str] = mapped_column(
        String(50),
        unique=True
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(60)
    )
    role: Mapped[Role] = mapped_column(
        Enum(Role, name='user_role'),
        default=Role.user
    )
    logged_with_provider: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment='External OAuth provider name user has registered with'
    )
    provider_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment='User\'s ID from OAuth provider user has registered with'
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=get_utc_now
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class Session(Base):
    __tablename__ = f'{Database.prefix}sessions'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Database.prefix}users.id', ondelete='CASCADE')
    )
    ip: Mapped[str] = mapped_column(
        String(15)
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
    is_closed: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    refresh_token_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        # TODO: consider adding unique constraint
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=get_utc_now
    )
    closed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class ConfirmationCode(Base):
    __tablename__ = f'{Database.prefix}confirmation_codes'
    id: Mapped[int] = mapped_column(  # TODO: consider replacing with uuid
        Integer,
        primary_key=True
    )
    code: Mapped[str] = mapped_column(
        String,
        unique=True,
        comment='The value of the code'
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    expired_at: Mapped[datetime.datetime] = mapped_column(
        DateTime
    )
    is_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=get_utc_now
    )


class Language(Base):
    __tablename__ = f'{Database.prefix}languages'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=True
    )
    iso_code: Mapped[str] = mapped_column(
        String,
        unique=True
    )


class Article(Base):
    __tablename__ = f'{Database.prefix}articles'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(
        String(50)
    )
    text: Mapped[str] = mapped_column(
        String(10240)
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    language_id: Mapped[int | None] = mapped_column(
        ForeignKey(f'{Language.__tablename__}.id', ondelete='CASCADE'),
        nullable=True
    )
    original_article_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(f'{Database.prefix}articles.id', ondelete='CASCADE'),
        nullable=True
    )
    like: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=get_utc_now
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class ReportReason(Base):
    __tablename__ = f'{Database.prefix}report_reasons'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    text: Mapped[str] = mapped_column(
        String,
        unique=True
    )
    order_position: Mapped[int] = mapped_column(
        Integer,
        unique=True
    )


class Report(Base):
    __tablename__ = f'{Database.prefix}reports'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    text: Mapped[str] = mapped_column(
        String(1024)
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Article.__tablename__}.id', ondelete='CASCADE')
    )
    status: Mapped[ReportStatus] = mapped_column(
        Enum(ReportStatus),
        default=ReportStatus.open
    )
    closed_by_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    original_article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Article.__tablename__}.id', ondelete='CASCADE')
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=get_utc_now
    )
    closed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class Comment(Base):
    __tablename__ = f'{Database.prefix}report_comments'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    text: Mapped[str] = mapped_column(
        String(100)
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Report.__tablename__}.id', ondelete='CASCADE')
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=get_utc_now
    )


class StylePrompt(Base):
    __tablename__ = f'{Database.prefix}style_prompts'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    title: Mapped[str] = mapped_column(
        String,
        unique=True
    )
    text: Mapped[str] = mapped_column(
        String,
        unique=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=get_utc_now
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class TranslationConfig(Base):
    __tablename__ = f'{Database.prefix}configs'
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            f'{StylePrompt.__tablename__}.id',
            ondelete='CASCADE'
        )
    )
    name: Mapped[str] = mapped_column(
        String(20),
        # TODO: add "unique for user" constraint
    )
    report_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Report.__tablename__}.id', ondelete='CASCADE')
    )
    language_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Report.__tablename__}.id', ondelete='CASCADE')
    ) # TODO: consider replacing with array (maybe JSONB or Array)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=get_utc_now
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class TranslationTask(Base):
    __tablename__ = f'{Database.prefix}translation_tasks'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    article_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Article.__tablename__}.id', ondelete='CASCADE')
    )
    source_language_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Language.__tablename__}.id', ondelete='CASCADE')
    )
    target_language_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{Language.__tablename__}.id', ondelete='CASCADE')
    )
    status: Mapped[TranslationTaskStatus] = mapped_column(
        Enum(TranslationTaskStatus),
        default=TranslationTaskStatus.started
    )
    translated_article_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(f'{Article.__tablename__}.id', ondelete='CASCADE'),
        nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=get_utc_now
    )
    deleted_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class Notification(Base):
    __tablename__ = f'{Database.prefix}notifications'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(
        String
    )
    text: Mapped[str] = mapped_column(
        String
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE')
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType)
    )
    read_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=get_utc_now
    )
