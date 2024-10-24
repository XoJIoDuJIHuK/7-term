from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.depends import get_session
from src.http_responses import get_responses
from src.responses import ListResponse, DataResponse, BaseResponse
from src.routers.config.schemes import ConfigOutScheme, CreateConfigScheme, \
    EditConfigScheme
from src.services.config import ConfigRepository
from src.util.auth.classes import JWTBearer
from src.util.auth.schemes import UserInfo

router = APIRouter(
    prefix='/configs',
    tags=['Configs']
)
config_not_found_error = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Конфиг не найден'
)


@router.get(
    '/',
    response_model=ListResponse[ConfigOutScheme],
    responses=get_responses(400, 401)
)
async def get_configs(
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
):
    configs = await ConfigRepository.get_list(
        user_id=user_info.id,
        db_session=db_session
    )
    return ListResponse(
        data={
            'list': configs
        }
    )


@router.post(
    '/',
    response_model=DataResponse.single_by_key(
        'config',
        ConfigOutScheme
    ),
    responses=get_responses(400, 401, 409)
)
async def create_config(
        config_data: CreateConfigScheme,
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
):
    config = await ConfigRepository.create(
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
        config_id: int = Path(),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
):
    config = await ConfigRepository.get_by_id(
        config_id=config_id,
        db_session=db_session
    )
    if not config:
        raise config_not_found_error
    config = await ConfigRepository.update(
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
    response_model=DataResponse.single_by_key(
        'config',
        ConfigOutScheme
    ),
    responses=get_responses(400, 401, 404, 409)
)
async def delete_config(
        config_id: int = Path(),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer())
):
    config = await ConfigRepository.get_by_id(
        config_id=config_id,
        db_session=db_session
    )
    if not config:
        raise config_not_found_error
    config = await ConfigRepository.delete(
        config=config,
        db_session=db_session
    )
    return BaseResponse(message=config.id)
