import datetime

from pydantic import BaseModel, EmailStr

from src.settings import Role


class EditUserScheme(BaseModel):
    name: str | None
    email: EmailStr | None
    email_verified: bool | None
    role: Role | None
    password: str | None

    class Config:
        from_attributes = True


class CreateUserScheme(EditUserScheme):
    logged_with_provider: str | None = None
    provider_id: str | None = None


class UserOutScheme(BaseModel):
    name: str
    email: EmailStr
    role: Role

    class Config:
        from_attributes = True


class UserOutAdminScheme(UserOutScheme):
    email_verified: bool
    logged_with_provider: str | None = None
    provider_id: str | None = None
    created_at: datetime.datetime
    deleted_at: datetime.datetime | None


class FilterUserScheme(BaseModel):
    email_verified: bool | None
    role: Role | None