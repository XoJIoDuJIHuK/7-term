import asyncio
import hashlib
import random

from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.database.models import (
    Role, User, Article, Report, ReportReason, Language, TranslationTask,
    TranslationTaskStatus, ReportStatus
)
from src.database.repos.language import LanguageRepo
from src.database.repos.model import ModelRepo
from src.database.repos.prompt import PromptRepo
from src.database.repos.report import ReportRepo


async def main():
    session: AsyncSession
    async with get_session() as session:
        user = User(
            name=hashlib.md5(b'lmao').hexdigest()[:20],
            email=f'{hashlib.md5(b'lmao').hexdigest()[:20]}@d.com',
            password_hash='',
            role=Role.user
        )
        session.add(user)
        await session.flush()
        original_article = Article(
            title='mock original',
            text='mock original text',
            user_id=user.id,
        )
        session.add(original_article)
        await session.flush()
        models = await ModelRepo.get_list(session)
        prompts = await PromptRepo.get_list(session)
        report_reasons = await ReportRepo.get_reasons_list(session)
        languages = await LanguageRepo.get_list(session)
        statuses = list(ReportStatus)
        for i in range(1000):
            model = random.choices(models)[0]
            report_reason = random.choices(report_reasons)[0]
            prompt = random.choices(prompts)[0]
            language = random.choices(languages)[0]
            report_status = random.choices(statuses)[0]

            translated_article = Article(
                title='translated article',
                text='translated article',
                user_id=user.id,
                original_article_id=original_article.id,
                language_id=language.id,
            )
            session.add(translated_article)
            await session.flush()
            translation_task = TranslationTask(
                article_id=original_article.id,
                target_language_id=language.id,
                prompt_id=prompt.id,
                model_id=model.id,
                status=TranslationTaskStatus.completed,
                translated_article_id=translated_article.id,
            )
            session.add(translation_task)
            await session.flush()
            report = Report(
                text='nonsense',
                article_id=translated_article.id,
                status=report_status,
                reason_id=report_reason.id,
            )
            session.add(report)
            await session.flush()
        await session.commit()
    print('Completed')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
