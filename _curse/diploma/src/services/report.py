import uuid

from fastapi import (
    HTTPException,
    status,
)

from src.database.helpers import build_where_clause
from src.database.models import (
    Report,
    ReportReason,
    ReportStatus,
    Comment, Article, User,
)
from src.pagination import PaginationParams, paginate
from src.routers.reports.schemes import (
    CreateReportScheme,
    EditReportScheme, CommentOutScheme, FilterReportsScheme, ReportOutScheme,
    ReportListItemScheme,
)

from sqlalchemy import select, exists, join, all_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.util.time.helpers import get_utc_now


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
    async def get_list(
            filter_params: FilterReportsScheme,
            pagination_params: PaginationParams,
            db_session: AsyncSession
    ) -> tuple[list[ReportListItemScheme], int]:
        query = select(Report).join(
            Article,
            Article.id == Report.article_id
        ).order_by(Report.created_at)
        user_id = filter_params.user_id
        filter_params.user_id = None
        if user_id is not None:
            query = query.where(user_id is None or Article.user_id == user_id)
        where_clause = build_where_clause(filter_params, Report)
        if where_clause is not None:
            query = query.where(where_clause)
        reports, count = await paginate(
            session=db_session,
            statement=query,
            pagination=pagination_params
        )
        return [ReportListItemScheme.create(r) for r in reports], count

    @staticmethod
    async def get_comments(
            article_id: uuid.UUID,
            db_session: AsyncSession
    ) -> list[CommentOutScheme]:
        result = await db_session.execute(
            select(Comment, User.name).select_from(
                join(
                    Comment,
                    Report,
                    Comment.report_id == Report.id
                )
                .join(
                    Article,
                    Report.article_id == Article.id
                )
                .outerjoin(User, Comment.sender_id == User.id)
            ).where(Article.id == article_id).order_by(Comment.created_at)
        )
        results = result.fetchall()
        return [
            CommentOutScheme(
                text=comment.text,
                sender_id=comment.sender_id,
                created_at=comment.created_at,
                sender_name=user_name
            ) for comment, user_name in results
        ]

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
        report = await db_session.execute(select(Report).filter_by(
            article_id=article_id
        ))
        return report.scalar_one_or_none()

    @classmethod
    async def create(
            cls,
            article_id: uuid.UUID,
            report_data: CreateReportScheme,
            db_session: AsyncSession
    ) -> Report:
        if await cls._report_exists(article_id, db_session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Жалоба на эту статью уже существует'
            )
        if not await cls._reason_exists(
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
        report.closed_at = get_utc_now()
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
