import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    status,
)

from src.depends import get_session
from src.database.models import Report, ReportStatus
from src.http_responses import get_responses
from src.responses import ListResponse, DataResponse
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
    '/report-reasons/',
    response_model=ListResponse[ReportReasonOutScheme]
)
async def get_report_reasons(
        db_session: AsyncSession = Depends(get_session)
):
    return ListResponse(
        data={
            'list': [
                ReportReasonOutScheme.model_validate(r) for r
                in await ReportRepository.get_reasons_list(db_session)
            ]
        }
    )


@router.get(
    '/{article_id}/report/'
)
async def get_report(
        report: Report | None = Depends(lambda: get_report(owner_only=False)),
        user_info: UserInfo = Depends(JWTBearer()),
):
    if not report:
        raise report_not_found_error
    return ReportOutScheme.model_validate(report)


@router.post(
    '/{article_id}/report/',
    response_model=DataResponse.single_by_key(
        'report',
        ReportOutScheme
    ),
    responses=get_responses(400, 401, 403, 409)
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
            status_code=status.HTTP_409_CONFLICT,
            detail='Жалоба на статью уже существует'
        )
    report = await ReportRepository.create(
        article_id=article_id,
        report_data=report_data,
        db_session=db_session
    )
    return DataResponse(
        data={
            'report': ReportOutScheme.model_validate(report)
        }
    )


@router.put(
    '/{article_id}/report/',
    response_model=DataResponse.single_by_key(
        'report',
        ReportOutScheme
    ),
    responses=get_responses(400, 401, 403, 404)
)
async def update_report(
        report_data: EditReportScheme,
        report: Report | None = Depends(lambda: get_report(owner_only=True)),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.user])),
):
    if not report:
        raise report_not_found_error
    report = await ReportRepository.update(
        report=report,  # TODO: do something with this (with what?)
        report_data=report_data,
        db_session=db_session
    )
    return DataResponse(
        data={
            'report': ReportOutScheme.model_validate(report)
        }
    )


@router.patch(
    '/{article_id}/report/status/',
    response_model=DataResponse.single_by_key(
        'report',
        ReportOutScheme
    ),
    responses=get_responses(400, 401, 403, 404)
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
    '/{article_id}/report/comments/',
    response_model=ListResponse[CommentOutScheme],
    responses=get_responses(400, 401, 403, 409)
)
async def get_comments(
        report: Report | None = Depends(lambda: get_report(owner_only=False)),
        user_info: UserInfo = Depends(JWTBearer(roles=[
            Role.user, Role.moderator
        ])),
):
    if not report:
        raise report_not_found_error
    return ListResponse(
        data={
            'list': [
                CommentOutScheme.model_validate(c) for c in report.comments
            ]
        }
    )


@router.post(
    '/{article_id}/report/comments/',
    response_model=DataResponse.single_by_key(
        'comment',
        CommentOutScheme
    ),
    responses=get_responses(400, 401, 403, 404)
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
    comment = await ReportRepository.create_comment(
        report_id=report.id,
        sender_id=user_info.id,
        text=comment_data.text,
        db_session=db_session
    )
    return DataResponse(
        data={
            'comment': CommentOutScheme.model_validate(comment)
        }
    )
