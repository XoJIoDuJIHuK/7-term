from fastapi import (
    Depends,
    HTTPException,
    Path,
    status,
)

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import StylePrompt
from src.depends import get_session
from src.services.prompt import PromptRepository


async def get_prompt(
        prompt_id: int = Path(),
        db_session: AsyncSession = Depends(get_session),
) -> StylePrompt:
    prompt = await PromptRepository.get_by_id(
        prompt_id=prompt_id,
        db_session=db_session
    )
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Промпт не найден'
        )
    return prompt
