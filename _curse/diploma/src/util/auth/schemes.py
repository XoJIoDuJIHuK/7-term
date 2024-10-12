import uuid

from pydantic import BaseModel, EmailStr, Field

from src.settings import Role


class UserInfo(BaseModel):
    id: uuid.UUID
    role: Role

    class Config:
        from_attributes = True


class LoginScheme(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=1024)


class TokensScheme(BaseModel):
    auth_token: str
    refresh_token: str

    class Config:
        from_attributes = True
