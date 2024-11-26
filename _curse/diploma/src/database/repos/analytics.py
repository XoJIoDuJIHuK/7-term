from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    AIModel,
    Article,
    Report,
    ReportReason,
    ReportStatus,
    TranslationTask, StylePrompt,
)


class AnalyticsRepo:
    @staticmethod
    async def get_prompts_stats(
            db_session: AsyncSession,
    ) -> dict:
        query = (
            select(StylePrompt.title, ReportStatus, func.count())
            .select_from(StylePrompt)
            .join(TranslationTask, TranslationTask.prompt_id == StylePrompt.id)
            .join(Article, Article.id == TranslationTask.translated_article_id)
            .join(Report, Report.article_id == Article.id)
            .join(ReportReason, ReportReason.id == Report.reason_id)
            .group_by(StylePrompt.title, Report.status)
            .order_by(StylePrompt.title, Report.status)
        )
        result = await db_session.execute(query)
        # TODO: try rewrite using defaultdicts
        ret = {}
        for prompt_title, report_status, rows_count in result.all():
            if prompt_title not in ret:
                ret[prompt_title] = {}
            statuses_dict = ret[prompt_title]

            statuses_dict[report_status] = rows_count
        return ret

    @staticmethod
    async def get_models_stats(
            db_session: AsyncSession,
    ) -> dict:
        query = (
            select(
                AIModel.provider, AIModel.name, Report.status, func.count()
            )
            .select_from(AIModel)
            .join(TranslationTask, TranslationTask.model_id == AIModel.id)
            .join(Article, Article.id == TranslationTask.translated_article_id)
            .join(Report, Report.article_id == Article.id)
            .join(ReportReason, ReportReason.id == Report.reason_id)
            .group_by(AIModel.provider, AIModel.name, Report.status)
            .order_by(AIModel.provider, AIModel.name, Report.status)
        )
        result = await db_session.execute(query)
        ret = {}
        for provider, model_name, report_status, rows_count in result.all():
            formatted_model_name = f'{provider} {model_name}'
            if formatted_model_name not in ret:
                ret[formatted_model_name] = {}
            statuses_dict = ret[formatted_model_name]

            statuses_dict[report_status] = rows_count
        return ret
