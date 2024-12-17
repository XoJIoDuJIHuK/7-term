import abc
from typing import Union

from fastapi import Request

from src.settings import (
    GoogleOauth2Config,
    MailOauth2Config,
    VKOauth2Config,
    YandexOauth2Config
)
from src.util.oauth.schemes import OAuthCredentialsScheme, OAuthUserInfoScheme
from src.util.storage.abstract import AbstractStorage


class BaseOauth2Authorize(abc.ABC):
    """
    Provides auxiliary methods for OAuth authentication flow
    """
    def __init__(
            self,
            config: Union[
                GoogleOauth2Config,
                VKOauth2Config,
                YandexOauth2Config,
                MailOauth2Config,
            ],
            credentials: OAuthCredentialsScheme,
            storage: AbstractStorage,
    ):
        self.config = config
        self.credentials = credentials
        self.storage = storage

    @abc.abstractmethod
    async def get_auth_url(
            self
    ) -> str:
        """
        Returns uri for user to redirect to for OAuth authentication flow
        """
        pass

    @abc.abstractmethod
    async def callback(
            self,
            request: Request
    ) -> str:
        """
        Exchanges auth code for access token at provider's API and returns
        token
        """
        pass

    @abc.abstractmethod
    async def get_user_info(
            self,
            access_token: str
    ) -> OAuthUserInfoScheme:
        """
        Returns info about user via access token
        """
        pass
