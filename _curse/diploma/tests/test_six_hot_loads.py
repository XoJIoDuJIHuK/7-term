import asyncio
import datetime
import logging

import httpx

import jwt

from sqlalchemy import delete, select

from src.database import get_session
from src.database.models import Article, TranslationConfig, User
from src.routers.articles.schemes import UploadArticleScheme
from src.routers.config.schemes import CreateConfigScheme
from src.settings import JWTConfig

from tests.hot_load import HotLoad


load = HotLoad(
    duration=datetime.timedelta(seconds=30),
    workers_number=1,
    processes_number=6,
)
api_url = 'http://localhost:8000/api/'
test_user_email = 'test@d.com'
user_agent = 'six hot loads'
jwt_config = JWTConfig()
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('tests.hot_load').setLevel(logging.WARNING)


@load.task
async def get_articles(client: httpx.AsyncClient, worker_id: int):
    response = await client.get(f'{api_url}articles/')
    response.raise_for_status()


@load.task
async def create_article(client: httpx.AsyncClient, worker_id: int):
    response = await client.post(
        f'{api_url}articles/',
        json=UploadArticleScheme(
            title=f'test article {worker_id}',
            text='text',
            language_id=None,
        ).model_dump(),
    )
    response.raise_for_status()
    article_id = response.json()['data']['article']['id']
    response = await client.delete(f'{api_url}articles/{article_id}/')
    response.raise_for_status()


@load.task
async def get_configs(client: httpx.AsyncClient, worker_id: int):
    response = await client.get(f'{api_url}configs/')
    response.raise_for_status()


@load.task
async def create_config(client: httpx.AsyncClient, worker_id: int):
    response = await client.post(
        f'{api_url}configs/',
        json=CreateConfigScheme(
            name=f'test config {worker_id}',
            model_id=None,
            prompt_id=None,
            language_ids=[],
        ).model_dump(),
    )
    response.raise_for_status()
    config_id = response.json()['data']['config']['id']
    response = await client.delete(f'{api_url}configs/{config_id}/')
    response.raise_for_status()


@load.on_startup
async def on_startup():
    headers = {}
    async with get_session() as session:
        user = (
            (
                await session.execute(
                    select(User).filter_by(email=test_user_email)
                )
            )
            .scalars()
            .first()
        )
        if user:
            await session.execute(
                delete(User).filter_by(email=test_user_email)
            )
        await session.flush()
        user = User(name='Test', email=test_user_email, password_hash='')
        session.add(user)
        await session.commit()
        await session.refresh(user)
        access_payload = {
            jwt_config.user_info_property: {
                'id': str(user.id),
                'user_agent': user_agent,
                'role': user.role.value,
            },
            'exp': 2**32 - 1,
        }
        access_token = jwt.encode(
            access_payload, jwt_config.secret_key, jwt_config.algorithm
        )
        headers['Cookie'] = f'access_token={access_token}'
        headers['User-Agent'] = user_agent
    return headers


@load.on_teardown
async def on_teardown():
    async with get_session() as session:
        user = (
            (
                await session.execute(
                    select(User).filter_by(email=test_user_email)
                )
            )
            .scalars()
            .first()
        )
        await session.execute(delete(Article).filter_by(user_id=user.id))
        await session.execute(
            delete(TranslationConfig).filter_by(user_id=user.id)
        )
        await session.execute(delete(User).filter_by(email=test_user_email))
        await session.commit()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(load.run())
    print(f'Mean RPS:', result)
