from fastapi import HTTPException, Request, status

import httpx

from src.database.repos.user import UserRepo
from src.database import get_session
from src.logger import get_logger
from src.util.common.helpers import generate_random_string

from src.settings import GoogleOauth2Config
from src.util.oauth.base import BaseOauth2Authorize
from src.util.oauth.schemes import OAuthCredentialsScheme, OAuthUserInfoScheme
from src.util.storage.abstract import AbstractStorage


logger = get_logger(__name__)


class GoogleOAuth2Authorize(BaseOauth2Authorize):
    def __init__(
            self,
            config: GoogleOauth2Config,
            credentials: OAuthCredentialsScheme,
            storage: AbstractStorage,
    ):
        super().__init__(config, credentials, storage)

    async def get_auth_url(
            self
    ) -> str:
        state = generate_random_string(16)

        await self.storage.set(
            self.__class__.__name__ + state, {'message': 'empty'}
        )

        authorization_url = (
            f'{self.config.AUTHORIZATION_URL}'
            f'?client_id={self.credentials.client_id}'
            f'&redirect_uri={self.config.REDIRECT_URI}&response_type='
            f'{self.config.response_type}&scope={self.config.SCOPE}'
            f'&state={state}'
        )

        return authorization_url

    async def callback(
            self,
            request: Request
    ) -> str:
        state = request.query_params.get('state', '')
        code = request.query_params.get('code', '')
        check_state = await self.storage.get(self.__class__.__name__ + state)

        if not check_state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Неправильное состояние'
            )

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.config.TOKEN_URL,
                data={
                    'grant_type': 'authorization_code',
                    'client_id': self.credentials.client_id,
                    'client_secret': self.credentials.client_secret,
                    'code': code,
                    'redirect_uri': self.config.REDIRECT_URI,
                },
                headers={'Accept': 'application/json'}
            )

        if response.status_code != 200 or 'error' in response.json():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Неправильный токен аутентификации'
            )

        return response.json().get('access_token')

    async def get_user_info(
            self,
            access_token: str
    ) -> OAuthUserInfoScheme:
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                f'{self.config.VALIDATE_URL}?access_token={access_token}'
            )

        user_data = user_response.json()
        logger.error('USER DATA', user_data)

        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Неправильный токен доступа'
            )

        email = user_data.get('email')
        async with get_session() as db_session:
            existing_user = await UserRepo.get_by_email(
                email, db_session
            )
            if existing_user:
                name = existing_user.name
            else:
                name = user_data.get('name') or generate_random_string(20)
                while await UserRepo.name_is_taken(name, db_session):
                    name = generate_random_string(20)

        return OAuthUserInfoScheme(
            id=user_data.get('sub'),
            email=email,
            name=name
        )
