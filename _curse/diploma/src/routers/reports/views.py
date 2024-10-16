import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    status,
)

from src.database import get_session
from src.database.models import Report, ReportStatus
from src.routers.reports.helpers import get_report
from src.routers.reports.schemes import (
    CommentOutScheme,
    CreateCommentScheme,
    CreateReportScheme,
    EditReportScheme,
    ReportOutScheme,
    ReportReasonOutScheme,
)
from src.services.report import ReportRepository
from src.settings import Role
from src.util.auth.classes import JWTBearer
from src.util.auth.schemes import UserInfo

from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix='/articles',
    tags=['Reports']
)
report_not_found_error = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='Жалоба не найдена'
)


@router.get(
    '/report-reasons/'
)
async def get_report_reasons(
        db_session: AsyncSession = Depends(get_session)
):
    return [
        ReportReasonOutScheme.model_validate(r) for r
        in await ReportRepository.get_reasons_list(db_session)
    ]


@router.get(
    '/{article_id}/report'
)
async def get_report(
        report: Report | None = Depends(lambda: get_report(owner_only=False)),
        user_info: UserInfo = Depends(JWTBearer()),
):
    if not report:
        raise report_not_found_error
    return ReportOutScheme.model_validate(report)


@router.post(
    '/{article_id}/report'
)
async def create_report(
        report_data: CreateReportScheme,
        report: Report | None = Depends(lambda: get_report(owner_only=True)),
        article_id: uuid.UUID = Path(),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.user])),
):

    if report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Жалоба на статью уже существует'
        )
    return ReportOutScheme.model_validate(
        await ReportRepository.create(
            article_id=article_id,
            report_data=report_data,
            db_session=db_session
        )
    )


@router.put(
    '/{article_id}/report/'
)
async def update_report(
        report_data: EditReportScheme,
        report: Report | None = Depends(lambda: get_report(owner_only=True)),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.user])),
):
    if not report:
        raise report_not_found_error
    return ReportOutScheme.model_validate(
        await ReportRepository.update(
            report=report,  # TODO: do something with this
            report_data=report_data,
            db_session=db_session
        )
    )


@router.patch(
    '/{article_id}/report/status/'
)
async def update_report_status(
        new_status: ReportStatus,
        article_id: uuid.UUID = Path(),
        report: Report | None = Depends(lambda: get_report(owner_only=False)),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer(roles=[
            Role.user, Role.moderator
        ])),
):
    if not report:
        raise report_not_found_error
    if report.status != ReportStatus.open:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Жалоба уже закрыта'
        )
    if (
        user_info.role == Role.user and new_status != ReportStatus.closed or
        user_info.role == Role.moderator and new_status not
        in [ReportStatus.rejected, ReportStatus.satisfied]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Действие запрещено'
        )
    return ReportOutScheme.model_validate(
        await ReportRepository.update_status(
            report=report,
            new_status=new_status,
            user_id=user_info.id,
            db_session=db_session
        )
    )


@router.get(
    '/{article_id}/report/comments/'
)
async def get_comments(
        report: Report | None = Depends(lambda: get_report(owner_only=False)),
        user_info: UserInfo = Depends(JWTBearer(roles=[
            Role.user, Role.moderator
        ])),
):
    if not report:
        raise report_not_found_error
    return [CommentOutScheme.model_validate(c) for c in report.comments]


@router.post(
    '/{article_id}/report/comments/'
)
async def create_comment(
        comment_data: CreateCommentScheme,
        report: Report | None = Depends(lambda: get_report(owner_only=False)),
        user_info: UserInfo = Depends(JWTBearer(roles=[
            Role.user, Role.moderator
        ])),
        db_session: AsyncSession = Depends(get_session)
):
    if not report:
        raise report_not_found_error
    return CommentOutScheme.model_validate(
        await ReportRepository.create_comment(
            report_id=report.id,
            sender_id=user_info.id,
            text=comment_data.text,
            db_session=db_session
        )
    )
