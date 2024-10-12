from passlib.context import CryptContext

from src.settings import AppConfig, JWTConfig


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_password_hash(password: str) -> str:
    password = f'{password}'
    return pwd_context.hash(password, salt=AppConfig.secret_key)
