from pydantic import EmailStr

from src.responses import Scheme


class SendEmailScheme(Scheme):
    to_address: EmailStr
    from_address: EmailStr
    from_name: str
    subject: str
    template_id: str
    params: dict | None = None
