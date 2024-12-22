import logging

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TranslationConfig
from src.depends import get_session
from src.http_responses import get_responses
from src.responses import (
    DataResponse,
    BaseResponse,
    SimpleListResponse,
)
from src.routers.config.helpers import get_config
from src.routers.config.schemes import (
    ConfigOutScheme,
    CreateConfigScheme, EditConfigScheme,
)
from src.database.repos.config import ConfigRepo
from src.settings import Role
from src.util.auth.classes import JWTCookie
from src.util.auth.schemes import UserInfo

router = APIRouter(
    prefix='/configs',
    tags=['Configs']
)
logger = logging.getLogger(__name__)


@router.get(
    '/',
    response_model=SimpleListResponse[ConfigOutScheme],
    responses=get_responses(400, 401)
)
async def get_configs(
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.user]))
):
    configs = await ConfigRepo.get_list(
        user_id=user_info.id,
        db_session=db_session
    )
    return SimpleListResponse[ConfigOutScheme].from_list(configs)


@router.post(
    '/',
    response_model=DataResponse.single_by_key(
        'config',
        ConfigOutScheme
    ),
    responses=get_responses(400, 401, 409)
)
async def create_config(
        request: Request,
        config_data: CreateConfigScheme,
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.user]))
):
    config = await ConfigRepo.create(
        config_data=config_data,
        user_id=user_info.id,
        db_session=db_session
    )
    return DataResponse(
        data={
            'config': ConfigOutScheme.model_validate(config)
        }
    )


@router.put(
    '/{config_id}/',
    response_model=DataResponse.single_by_key(
        'config',
        ConfigOutScheme
    ),
    responses=get_responses(400, 401, 404, 409)
)
async def update_config(
        config_data: EditConfigScheme,
        config: TranslationConfig = Depends(get_config),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.user]))
):
    config = await ConfigRepo.update(
        config=config,
        new_data=config_data,
        db_session=db_session
    )
    return DataResponse(
        data={
            'config': ConfigOutScheme.model_validate(config)
        }
    )


@router.delete(
    '/{config_id}/',
    response_model=BaseResponse,
    responses=get_responses(400, 401, 404, 409)
)
async def delete_config(
        request: Request,
        config: TranslationConfig = Depends(get_config),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.user]))
):
    logger.info(f'Worker {request.headers.get('X-Worker-ID', 'unknown')} is trying to delete config {config.name[-1]}')
    config_name = config.name
    await ConfigRepo.delete(
        config=config,
        db_session=db_session
    )
    return BaseResponse(message=f'Конфиг {config_name} удалён')
