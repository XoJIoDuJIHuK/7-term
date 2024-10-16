import uuid

from fastapi import (
    HTTPException,
    status,
)

from src.database.models import (
    Report,
    ReportReason,
    ReportStatus,
    Comment,
)
from src.routers.reports.schemes import (
    CreateReportScheme,
    EditReportScheme,
)
from src.services.article import ArticleRepository

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession


class ReportRepository:
    @staticmethod
    async def get_reasons_list(
            db_session: AsyncSession
    ) -> list[ReportReason]:
        result = await db_session.execute(select(ReportReason).order_by(
            ReportReason.order_position
        ))
        return [r for r in result.scalars().all()]

    @staticmethod
    async def _reason_exists(
            reason_id: int,
            db_session: AsyncSession
    ) -> bool:
        result = await db_session.execute(
            select(exists().where(ReportReason.id == reason_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _report_exists(
            article_id: uuid.UUID,
            db_session: AsyncSession
    ) -> bool:
        result = await db_session.execute(
            select(exists().where(Report.article_id == article_id))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_article_id(
            article_id: uuid.UUID,
            db_session: AsyncSession
    ) -> Report | None:
        article = await ArticleRepository.get_by_id(
            article_id=article_id,
            db_session=db_session
        )
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Статья не найдена'
            )
        return article.report

    @staticmethod
    async def create(
            article_id: uuid.UUID,
            report_data: CreateReportScheme,
            db_session: AsyncSession
    ) -> Report:
        # TODO: consider extracting logic from repository
        if ReportRepository._report_exists(article_id, db_session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Жалоба на эту статью уже существует'
            )
        if not await ReportRepository._reason_exists(
            reason_id=report_data.reason_id,
            db_session=db_session
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Причина жалобы не найдена'
            )

        report = Report(
            text=report_data.text,
            article_id=article_id,
            reason_id=report_data.reason_id
        )
        db_session.add(report)
        await db_session.commit()
        await db_session.refresh(report)
        return report

    @staticmethod
    async def update(
            report: Report,
            report_data: EditReportScheme,
            db_session: AsyncSession,
    ) -> Report:
        report.text = report_data.text
        report.reason_id = report_data.reason_id
        db_session.add(report)
        await db_session.commit()
        await db_session.refresh(report)
        return report

    @staticmethod
    async def update_status(
            report: Report,
            new_status: ReportStatus,
            user_id: uuid.UUID,
            db_session: AsyncSession
    ) -> Report:
        report.status = new_status
        report.closed_by_user_id = user_id
        db_session.add(report)
        await db_session.commit()
        await db_session.refresh(report)
        return report

    @staticmethod
    async def create_comment(
            report_id: uuid.UUID,
            text: str,
            sender_id: uuid.UUID,
            db_session: AsyncSession
    ) -> Comment:
        comment = Comment(
            text=text,
            sender_id=sender_id, # TODO: add efficient checks or foreign key violation errors handling
            report_id=report_id
        )
        db_session.add(comment)
        await db_session.commit()
        await db_session.refresh(comment)
        return comment
