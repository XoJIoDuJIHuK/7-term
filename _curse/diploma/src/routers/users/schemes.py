import datetime
import uuid

from pydantic import EmailStr, Field

from src.responses import Scheme
from src.settings import Role


class UserUpdateNameScheme(Scheme):
    name: str = Field(min_length=1, max_length=20)


class EditUserScheme(Scheme):
    name: str | None
    email: EmailStr | None
    email_verified: bool | None
    role: Role | None
    password: str | None


class CreateUserScheme(EditUserScheme):
    # TODO: change types
    logged_with_provider: str | None = None
    provider_id: str | None = None


class UserOutScheme(Scheme):
    id: uuid.UUID
    name: str
    email: EmailStr
    email_verified: bool
    role: Role


class UserOutAdminScheme(UserOutScheme):
    email_verified: bool
    logged_with_provider: str | None = None
    provider_id: str | None = None
    created_at: datetime.datetime
    deleted_at: datetime.datetime | None


class FilterUserScheme(Scheme):
    email_verified: bool | None
    role: Role | None
