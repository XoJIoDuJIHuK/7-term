from pydantic import Field

from src.responses import Scheme
from src.util.auth.schemes import LoginScheme


class ResetPasswordScheme(Scheme):
    new_password: str = Field(min_length=1, max_length=1024)
    code: str



class RegistrationScheme(LoginScheme):
    name: str = Field(min_length=1, max_length=20)