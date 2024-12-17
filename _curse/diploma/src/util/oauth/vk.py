import base64
import hashlib
import random
import string

from fastapi import HTTPException, Request, status

import httpx

from src.settings import VKOauth2Config
from src.util.common.helpers import generate_random_string
from src.util.oauth.base import BaseOauth2Authorize
from src.util.oauth.schemes import OAuthCredentialsScheme, OAuthUserInfoScheme
from src.util.storage.abstract import AbstractStorage


class VkOAuth2Authorize(BaseOauth2Authorize):
    def __init__(
            self,
            config: VKOauth2Config,
            credentials: OAuthCredentialsScheme,
            storage: AbstractStorage,
    ):
        super().__init__(config, credentials, storage)

    async def get_auth_url(
            self
    ) -> str:
        state = generate_random_string(16)

        code_verifier = ''.join(
            random.choices(string.ascii_letters + string.digits, k=64)
        )

        await self.storage.set(
            self.__class__.__name__ + state,
            {'code_verifier': code_verifier}
        )

        sha256_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()

        code_challenge = base64.urlsafe_b64encode(sha256_hash).decode(
            'utf-8').rstrip('=')

        authorization_url = (
            f'{self.config.AUTHORIZATION_URL}'
            f'?client_id={self.credentials.client_id}'
            f'&redirect_uri={self.config.REDIRECT_URI}&response_type='
            f'{self.config.response_type}&scope={self.config.SCOPE}'
            f'&state={state}&code_challenge={code_challenge}'
            f'&code_challenge_method=S256'
        )

        return authorization_url

    async def callback(
            self,
            request: Request
    ) -> str:
        """
        Exchanges auth code for access token at provider's API and returns
        token
        """
        state = request.query_params.get('state', '')
        code = request.query_params.get('code')
        device_id = request.query_params.get('device_id')
        state_params = await self.storage.get(self.__class__.__name__ + state)

        if not state_params:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Неправильное состояние'
            )

        code_verifier = state_params.get('code_verifier')

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.config.TOKEN_URL,
                data={
                    'grant_type': 'authorization_code',
                    'client_id': self.credentials.client_id,
                    'device_id': device_id,
                    'code': code,
                    'redirect_uri': self.config.REDIRECT_URI,
                    'code_verifier': code_verifier,
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
            user_response = await client.post(
                self.config.VALIDATE_URL,
                data={
                    'access_token': access_token,
                    'client_id': self.credentials.client_id,
                    'v': self.config.API_VERSION,
                },
                headers={'Accept': 'application/json'}
            )

            user_data = user_response.json().get('response')[0]

            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='Неправильный токен доступа'
                )

            return OAuthUserInfoScheme(
                id=user_data.get('id'),
                email=user_data.get('email', None)
            )
