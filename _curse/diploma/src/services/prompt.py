from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import StylePrompt
from src.routers.prompts.schemes import PromptOutScheme, CreatePromptScheme
from src.util.db.helpers import update_object
from src.util.time.helpers import get_utc_now


class PromptRepository:
    @staticmethod
    async def exists_by_id(
            prompt_id: int,
            db_session: AsyncSession
    ) -> bool:
        result = await db_session.execute(select(exists().where(
            StylePrompt.id == prompt_id,
            StylePrompt.deleted_at.is_(None)
        )))
        return result.scalar_one_or_none()

    @staticmethod
    async def exists_by_title(
            title: str,
            db_session: AsyncSession
    ) -> bool:
        result = await db_session.execute(select(exists().where(
            StylePrompt.title == title,
            StylePrompt.deleted_at.is_(None)
        )))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_list(
            db_session: AsyncSession
    ) -> list[PromptOutScheme]:
        result = await db_session.execute(select(StylePrompt).where(
            StylePrompt.deleted_at.is_(None)
        ))
        return [
            PromptOutScheme.model_validate(p) for p in result.scalars().all()
        ]

    @staticmethod
    async def get_by_id(
            prompt_id: int,
            db_session: AsyncSession
    ) -> StylePrompt | None:
        result = await db_session.execute(select(StylePrompt).filter_by(
            id=prompt_id
        ))
        return result.scalar_one_or_none()

    @classmethod
    async def create(
            cls,
            prompt_data: CreatePromptScheme,
            db_session: AsyncSession
    ) -> StylePrompt:
        if await cls.exists_by_title(
            title=prompt_data.title,
            db_session=db_session
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Название промпта занято'
            )
        prompt = StylePrompt(
            title=prompt_data.title,
            text=prompt_data.text,
        )
        db_session.add(prompt)
        await db_session.commit()
        await db_session.refresh(prompt)
        return prompt

    @classmethod
    async def update(
            cls,
            prompt: StylePrompt,
            prompt_data: CreatePromptScheme,
            db_session: AsyncSession
    ) -> StylePrompt:
        if prompt_data.title is not None and await cls.exists_by_title(
                title=prompt_data.title,
                db_session=db_session
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Название промпта занято'
            )
        prompt = update_object(
            db_object=prompt,
            update_scheme=prompt_data
        )
        db_session.add(prompt)
        await db_session.commit()
        await db_session.refresh(prompt)
        return prompt

    @staticmethod
    async def delete(
            prompt: StylePrompt,
            db_session: AsyncSession
    ) -> StylePrompt:
        prompt.deleted_at = get_utc_now()
        db_session.add(prompt)
        await db_session.commit()
        await db_session.refresh(prompt)
        return prompt
