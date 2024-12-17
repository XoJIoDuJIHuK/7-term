from src.responses import Scheme


class OAuthCredentialsScheme(Scheme):
    client_id: str
    client_secret: str


class OAuthUserInfoScheme(Scheme):
    id: str
    email: str
    name: str
