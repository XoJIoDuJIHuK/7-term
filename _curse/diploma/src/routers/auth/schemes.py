from pydantic import Field

from src.util.auth.schemes import LoginScheme


class RegistrationScheme(LoginScheme):
    name: str = Field(min_length=1, max_length=20)