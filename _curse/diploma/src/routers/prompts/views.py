from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import StylePrompt
from src.depends import get_session
from src.responses import SimpleListResponse, DataResponse, BaseResponse
from src.routers.prompts.helpers import get_prompt
from src.routers.prompts.schemes import PromptOutScheme, CreatePromptScheme, \
    EditPromptScheme, PromptOutAdminScheme
from src.database.repos.prompt import PromptRepo
from src.settings import Role
from src.util.auth.classes import JWTCookie
from src.util.auth.schemes import UserInfo

router = APIRouter(
    prefix='/prompts',
    tags=['Prompts']
)


@router.get(
    '/',
    response_model=SimpleListResponse[PromptOutAdminScheme],
)
async def get_admin_prompts(
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin]))
):
    prompts = await PromptRepo.get_list(
        db_session=db_session
    )
    return SimpleListResponse[PromptOutAdminScheme].from_list(items=[
        PromptOutAdminScheme.model_validate(p) for p in prompts
    ])


@router.get(
    '/public/',
    response_model=SimpleListResponse[PromptOutScheme],
)
async def get_prompts(
        db_session: AsyncSession = Depends(get_session)
):
    prompts = await PromptRepo.get_list(
        db_session=db_session
    )
    return SimpleListResponse[PromptOutScheme].from_list(items=[
        PromptOutScheme.model_validate(p) for p in prompts
    ])


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
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin]))
):
    prompt = await PromptRepo.create(
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
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin]))
):
    prompt = await PromptRepo.update(
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
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.admin]))
):
    await PromptRepo.delete(
        prompt=prompt,
        db_session=db_session
    )
    return BaseResponse(message='Промпт удалён')