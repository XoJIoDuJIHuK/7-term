from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import StylePrompt
from src.depends import get_session
from src.responses import SimpleListResponse, DataResponse, BaseResponse
from src.routers.prompts.helpers import get_prompt
from src.routers.prompts.schemes import PromptOutScheme, CreatePromptScheme, \
    EditPromptScheme
from src.services.prompt import PromptRepository
from src.settings import Role
from src.util.auth.classes import JWTBearer
from src.util.auth.schemes import UserInfo

router = APIRouter(
    prefix='/prompts',
    tags=['Prompts']
)


@router.get(
    '/',
    response_model=SimpleListResponse[PromptOutScheme],
)
async def get_prompts(
        db_session: AsyncSession = Depends(get_session)
):
    prompts = await PromptRepository.get_list(
        db_session=db_session
    )
    return SimpleListResponse[PromptOutScheme].from_list(items=prompts)


@router.post(
    '/',
    response_model=DataResponse.single_by_key(
        'prompt',
        PromptOutScheme
    )
)
async def create_prompt(
        prompt_data: CreatePromptScheme,
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.admin]))
):
    prompt = await PromptRepository.create(
        prompt_data=prompt_data,
        db_session=db_session
    )
    return DataResponse(
        data={
            'prompt': PromptOutScheme.model_validate(prompt)
        }
    )


@router.put(
    '/{prompt_id}/',
    response_model=DataResponse.single_by_key(
        'prompt',
        PromptOutScheme
    )
)
async def update_prompt(
        prompt_data: EditPromptScheme,
        prompt: StylePrompt = Depends(get_prompt),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.admin]))
):
    prompt = await PromptRepository.update(
        prompt=prompt,
        prompt_data=prompt_data,
        db_session=db_session
    )
    return DataResponse(
        data={
            'prompt': PromptOutScheme.model_validate(prompt)
        }
    )


@router.delete(
    '/{prompt_id}/',
    response_model=BaseResponse
)
async def delete_prompt(
        prompt: StylePrompt = Depends(get_prompt),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.admin]))
):
    await PromptRepository.delete(
        prompt=prompt,
        db_session=db_session
    )
    return BaseResponse(message='Промпт удалён')