import datetime

from pydantic import BaseModel, EmailStr

from src.settings import Role


class EditUserScheme(BaseModel):
    name: str
    email: EmailStr
    email_verified: bool = False
    role: Role
    password_hash: str

    class Config:
        from_attributes = True


class CreateUserScheme(EditUserScheme):
    logged_with_provider: str | None = None
    provider_id: str | None = None


class UserOutScheme(CreateUserScheme):
    created_at: datetime.datetime
    deleted_at: datetime.datetime | None = None


class FilterUserScheme(BaseModel):
    name: str
    email: EmailStr
    email_verified: bool = False
    role: Role