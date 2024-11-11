import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import TranslationTask
from src.routers.translation.schemes import CreateTaskScheme


class TaskRepo:
    @staticmethod
    async def get_by_id(
            task_id: uuid.UUID,
            db_session: AsyncSession
    ) -> TranslationTask | None:
        result = await db_session.execute(select(TranslationTask).where(
            TranslationTask.id == task_id,
            TranslationTask.deleted_at.is_(None)
        ))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
            task_data: CreateTaskScheme,
            db_session: AsyncSession
    ) -> TranslationTask:
        task = TranslationTask(
            article_id=task_data.article_id,
            target_language_id=task_data.target_language_id,
            model_id=task_data.model_id,
            prompt_id=task_data.prompt_id
        )
        db_session.add(task)
        await db_session.commit()
        await db_session.refresh(task)
        return task