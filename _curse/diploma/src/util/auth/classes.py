import uuid

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Session, User
from src.settings import JWTConfig, Role
from src.util.auth.schemes import TokensScheme, UserInfo
from src.util.time.helpers import get_utc_now


class JWTBearer(HTTPBearer):
    def __init__(
            self,
            roles: list[Role] = None,
            auto_error: bool = True
    ):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.roles = roles if roles else []

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials
        try:
            credentials = await (
                super(JWTBearer, self).__call__(request)
            )
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Wrong credentials'
            )

        error_invalid_token = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid token'
        )
        error_no_rights = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Insufficient privileges'
        )

        if credentials:
            if not credentials.scheme == 'Bearer':
                raise error_invalid_token
            if not (
                    payload := await self.verify_jwt(credentials.credentials)
            ):
                raise error_invalid_token

            provided_role = payload.role
            if not await self.role_allowed(provided_role):
                raise error_no_rights

            return payload
        else:
            return None

    async def verify_jwt(self, token: str) -> UserInfo:
        try:
            payload = jwt.decode(
                token, JWTConfig.secret_key, algorithms=[JWTConfig.algorithm]
            )
            return JWTBearer.get_payload(payload)
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Неправильный токен'
            )

    @staticmethod
    async def check_session(
            session_id: str,
            payload: UserInfo
    ):
        # TODO: implement using Redis (if allowed by Smelov)
        return True

    async def role_allowed(self, provided_role: Role) -> bool:
        if len(self.roles) == 0:
            return True
        if not provided_role:
            return False
        return provided_role in self.roles

    @staticmethod
    def get_payload(dict_payload: dict) -> UserInfo:
        try:
            print(dict_payload.get(JWTConfig.user_info_property))
            return UserInfo(**dict_payload.get(JWTConfig.user_info_property))
        except Exception as e:
            print(e)
            raise Exception(e)


class AuthHandler:
    @classmethod
    async def login(
            cls,
            user: User,
            request: Request,
            db_session: AsyncSession
    ) -> TokensScheme:
        refresh_token_id = uuid.uuid4()
        session = Session(
            user_id=user.id,
            refresh_token_id=refresh_token_id,
            ip=request.client.host
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)
        await db_session.refresh(user)
        return cls.get_tokens(
            user_id=user.id,
            session_id=session.id,
            role=user.role,
            refresh_token_id=refresh_token_id
        )


    @classmethod
    def get_tokens(
            cls,
            user_id: uuid.UUID,
            session_id: uuid.UUID,
            role: Role,
            refresh_token_id: uuid.UUID
    ) -> TokensScheme:
        auth_payload = {
            JWTConfig.user_info_property: {
                'id': str(user_id),
                'role': role.value,
            },
            'exp': get_utc_now() + JWTConfig.auth_jwt_exp_sec
        }
        refresh_payload = {
            'user_id': str(user_id),
            'session_id': str(session_id),
            'token_id': str(refresh_token_id),
            'exp': get_utc_now() + JWTConfig.refresh_jwt_exp_sec
        }
        return TokensScheme(
            auth_token=jwt.encode(
                auth_payload, JWTConfig.secret_key, JWTConfig.algorithm
            ),
            refresh_token=jwt.encode(
                refresh_payload, JWTConfig.secret_key, JWTConfig.algorithm
            )
        )

