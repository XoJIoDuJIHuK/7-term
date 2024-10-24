from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.depends import get_session
from src.responses import SimpleListResponse
from src.routers.prompts.schemes import PromptOutScheme
from src.services.prompt import PromptRepository

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
