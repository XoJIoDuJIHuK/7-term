import asyncio
import sys
from typing import Optional

import click

from src.database import get_session

from src.util.auth.helpers import get_password_hash
from src.util.time.helpers import get_utc_now

from src.database.models import User
from src.settings import Role

from sqlalchemy import select


@click.command()
@click.option('-pw', '--password', help='Password of user', default='string')
@click.option('-e', '--email', help='Email of user', default='user@d.com')
@click.option('-n', '--name', help='Name of user', default='Admin')
def create_admin(
        name: str,
        password: str,
        email: str,
) -> None:
    async def async_function() -> Optional[str]:
        """
        Asynchronous function that handles the creation or update of an admin
        """
        session_generator = get_session()

        db_session = await anext(session_generator)

        try:
            user = (await db_session.execute(select(User).where(
                User.email == email
            ))).scalars().first()

            if user:
                return 'Email is taken'

            hashed_password = get_password_hash(password)

            if user:
                user.email = email
                user.password_hash = hashed_password
            else:
                user = User(
                    name=name,
                    email=email,
                    email_verified=True,
                    role=Role.admin,
                    password_hash=hashed_password,
                    created_at=get_utc_now(),
                    deleted_at=None
                )
            db_session.add(user)
            await db_session.commit()
            await db_session.refresh(user)
            return 'User created'
        finally:
            await db_session.close()
            await session_generator.aclose()

    loop = asyncio.get_event_loop()
    try:
        result = loop.run_until_complete(async_function())
        click.echo(result)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
    sys.exit()