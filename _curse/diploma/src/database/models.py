import datetime
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
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


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
    role_id: Mapped[Role] = mapped_column(
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



