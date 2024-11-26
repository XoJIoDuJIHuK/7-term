import uuid

from pydantic import EmailStr, Field

from src.responses import Scheme
from src.settings import Role


class UserInfo(Scheme):
    id: uuid.UUID
    user_agent: str
    role: Role


class RefreshPayload(UserInfo):
    session_id: uuid.UUID
    token_id: uuid.UUID


class LoginScheme(Scheme):
    email: EmailStr = Field(examples=['user@d.com'])
    password: str = Field(min_length=1, max_length=1024)


class TokensScheme(Scheme):
    access_token: str
    refresh_token: str
