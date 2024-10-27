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
from src.pagination import PaginationParams, get_pagination_params
from src.responses import ListResponse, DataResponse, SimpleListResponse, \
    BaseResponse
from src.routers.reports.helpers import get_report
from src.routers.reports.schemes import (
    CommentOutScheme,
    CreateCommentScheme,
    CreateReportScheme,
    EditReportScheme,
    ReportOutScheme,
    ReportReasonOutScheme, FilterReportsScheme, ReportListItemScheme,
)
from src.services.report import ReportRepository
from src.settings import Role
from src.util.auth.classes import JWTBearer
from src.util.auth.schemes import UserInfo

from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix='',
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
    '/reports/'
)
async def get_reports(
        report_status: ReportStatus | None = None,
        user_id: uuid.UUID | None = None,
        article_id: uuid.UUID | None = None,
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.moderator])),
        pagination_params: PaginationParams = Depends(get_pagination_params),
        db_session: AsyncSession = Depends(get_session)
):
    reports, count = await ReportRepository.get_list(
        filter_params=FilterReportsScheme(
            status=report_status,
            user_id=user_id,
            article_id=article_id
        ),
        pagination_params=pagination_params,
        db_session=db_session
    )
    return ListResponse[ReportListItemScheme].from_list(
        items=reports,
        total_count=count,
        params=pagination_params
    )


@router.get(
    '/articles/{article_id}/report/'
)
async def get_article_report(
        report: Report | None = Depends(get_report(owner_only=False)),
        user_info: UserInfo = Depends(JWTBearer()),
):
    if not report:
        raise report_not_found_error
    return ReportOutScheme.create(report)


@router.post(
    '/articles/{article_id}/report/',
    response_model=DataResponse.single_by_key(
        'report',
        ReportOutScheme
    ),
    responses=get_responses(400, 401, 403, 409)
)
async def create_report(
        report_data: CreateReportScheme,
        report: Report | None = Depends(get_report(owner_only=True)),
        article_id: uuid.UUID = Path(),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.user])),
):
    report = await ReportRepository.create(
        article_id=article_id,
        report_data=report_data,
        db_session=db_session
    )
    return DataResponse(
        data={
            'report': ReportOutScheme.create(report)
        }
    )


@router.put(
    '/articles/{article_id}/report/',
    response_model=DataResponse.single_by_key(
        'report',
        ReportOutScheme
    ),
    responses=get_responses(400, 401, 403, 404)
)
async def update_report(
        report_data: EditReportScheme,
        report: Report | None = Depends(get_report(owner_only=True)),
        db_session: AsyncSession = Depends(get_session),
        user_info: UserInfo = Depends(JWTBearer(roles=[Role.user])),
):
    if not report:
        raise report_not_found_error
    report = await ReportRepository.update(
        report=report,
        report_data=report_data,
        db_session=db_session
    )
    return DataResponse(
        data={
            'report': ReportOutScheme.create(report)
        }
    )


@router.patch(
    '/articles/{article_id}/report/status/',
    response_model=DataResponse.single_by_key(
        'report',
        ReportOutScheme
    ),
    responses=get_responses(400, 401, 403, 404)
)
async def update_report_status(
        new_status: ReportStatus,
        article_id: uuid.UUID = Path(),
        report: Report | None = Depends(get_report(owner_only=False)),
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
    return DataResponse(
        data={
            'report': ReportOutScheme.create(
                await ReportRepository.update_status(
                    report=report,
                    new_status=new_status,
                    user_id=user_info.id,
                    db_session=db_session
                )
            )
        }
    )


@router.get(
    '/articles/{article_id}/report/comments/',
    response_model=SimpleListResponse[CommentOutScheme],
    responses=get_responses(400, 401, 403, 409)
)
async def get_comments(
        report: Report | None = Depends(get_report(owner_only=False)),
        user_info: UserInfo = Depends(JWTBearer(roles=[
            Role.user, Role.moderator
        ])),
        db_session: AsyncSession = Depends(get_session)
):
    if not report:
        raise report_not_found_error
    return SimpleListResponse[CommentOutScheme].from_list(
        await ReportRepository.get_comments(
            article_id=report.article_id,
            db_session=db_session
        )
    )


@router.post(
    '/articles/{article_id}/report/comments/',
    response_model=BaseResponse,
    responses=get_responses(400, 401, 403, 404)
)
async def create_comment(
        comment_data: CreateCommentScheme,
        report: Report | None = Depends(get_report(owner_only=False)),
        user_info: UserInfo = Depends(JWTBearer(roles=[
            Role.user, Role.moderator
        ])),
        db_session: AsyncSession = Depends(get_session)
):
    if not report or report.status != ReportStatus.open:
        raise report_not_found_error
    # await db_session.refresh(report)
    await ReportRepository.create_comment(
        report_id=report.id,
        sender_id=user_info.id,
        text=comment_data.text,
        db_session=db_session
    )
    return BaseResponse()
