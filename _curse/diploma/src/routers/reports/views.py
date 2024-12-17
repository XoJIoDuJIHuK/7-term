import asyncio
import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    WebSocket,
    status,
)
from starlette.websockets import WebSocketDisconnect

from src.depends import get_session, validate_token_for_ws
from src.database.models import Report, ReportStatus
from src.http_responses import get_responses
from src.logger import get_logger
from src.pagination import PaginationParams, get_pagination_params
from src.responses import ListResponse, DataResponse, SimpleListResponse
from src.routers.reports.helpers import get_report
from src.routers.reports.schemes import (
    CommentOutScheme,
    CreateCommentScheme,
    CreateReportScheme,
    EditReportScheme,
    ReportOutScheme,
    ReportReasonOutScheme,
    FilterReportsScheme,
    ReportListItemScheme,
    ReportOutModScheme,
)
from src.database.repos.article import ArticleRepo
from src.database.repos.report import ReportRepo
from src.database.repos.user import UserRepo
from src.settings import Role
from src.util.auth.classes import JWTCookie
from src.util.auth.schemes import UserInfo

from sqlalchemy.ext.asyncio import AsyncSession

from src.util.storage.classes import RedisHandler

logger = get_logger(__name__)
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
    response_model=SimpleListResponse[ReportReasonOutScheme]
)
async def get_report_reasons(
        db_session: AsyncSession = Depends(get_session)
):
    return SimpleListResponse[ReportReasonOutScheme].from_list(
        items=[
            ReportReasonOutScheme.model_validate(r) for r
            in await ReportRepo.get_reasons_list(db_session)
        ]
    )


@router.get(
    '/reports/',
    response_model=ListResponse[ReportListItemScheme]
)
async def get_reports(
        report_status: ReportStatus | None = None,
        user_id: uuid.UUID | None = None,
        article_id: uuid.UUID | None = None,
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.moderator])),
        pagination_params: PaginationParams = Depends(get_pagination_params),
        db_session: AsyncSession = Depends(get_session)
):
    reports, count = await ReportRepo.get_list(
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
    '/articles/{article_id}/report/',
)
async def get_article_report(
        report: Report | None = Depends(get_report(owner_only=False)),
        user_info: UserInfo = Depends(JWTCookie()),
        db_session: AsyncSession = Depends(get_session),
):
    if not report:
        raise report_not_found_error
    if user_info.role == Role.user:
        return DataResponse(
            data={
                'report': ReportOutScheme.create(report)
            }
        )

    translated_article = await ArticleRepo.get_by_id(
        article_id=report.article_id,
        db_session=db_session
    )
    source_article = await ArticleRepo.get_by_id(
        article_id=translated_article.original_article_id,
        db_session=db_session
    )
    return DataResponse(
        data={
            'report': ReportOutModScheme.create(
                report,
                source_text=source_article.text,
                source_language_id=source_article.language_id,
                translated_text=translated_article.text,
                translated_language_id=translated_article.language_id,
            )
        }
    )



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
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.user])),
):
    article = await ArticleRepo.get_by_id(
        article_id=article_id,
        db_session=db_session
    )
    if article.original_article_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Жаловаться можно только на переводы'
        )
    report = await ReportRepo.create(
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
        user_info: UserInfo = Depends(JWTCookie(roles=[Role.user])),
):
    if not report:
        raise report_not_found_error
    report = await ReportRepo.update(
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
        user_info: UserInfo = Depends(JWTCookie(roles=[
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
                await ReportRepo.update_status(
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
        user_info: UserInfo = Depends(JWTCookie(roles=[
            Role.user, Role.moderator
        ])),
        db_session: AsyncSession = Depends(get_session)
):
    if not report:
        raise report_not_found_error
    return SimpleListResponse[CommentOutScheme].from_list(
        await ReportRepo.get_comments(
            article_id=report.article_id,
            db_session=db_session
        )
    )


@router.websocket(
    '/articles/{article_id}/report/comments/ws/',
)
async def watch_for_comments(
        websocket: WebSocket,
        user_info: UserInfo = Depends(validate_token_for_ws),
        article_id: uuid.UUID = Path(),
        db_session: AsyncSession = Depends(get_session),
):
    article = await ArticleRepo.get_by_id(
        article_id=article_id,
        db_session=db_session
    )
    if not article or article.user_id != user_info.id and user_info.role != Role.moderator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Жалоба не найдена'
        )

    try:
        await websocket.accept()

        pubsub = RedisHandler().get_pubsub()
        await pubsub.subscribe(f'comments_{str(article_id)}')
        while True:
            try:
                message = await pubsub.get_message(timeout=0.5)
                if message and message['type'] == 'message':
                    comment_data = message['data'].decode('utf-8')
                    try:
                        comment_scheme = CommentOutScheme.model_validate_json(
                            comment_data
                        )
                        await websocket.send(
                            comment_scheme.model_dump_json(exclude_unset=True)
                        )
                    except Exception as e:
                        logger.exception(e)
                await asyncio.sleep(0)

            except Exception as e:
                logger.exception(e)
                break

    except WebSocketDisconnect:
        logger.error(f'WebSocket connection closed')
    except Exception as e:
        logger.exception(e)
        await websocket.close()


@router.post(
    '/articles/{article_id}/report/comments/',
    response_model=DataResponse.single_by_key(
        'comment',
        CommentOutScheme
    ),
    responses=get_responses(400, 401, 403, 404)
)
async def create_comment(
        comment_data: CreateCommentScheme,
        report: Report | None = Depends(get_report(owner_only=False)),
        user_info: UserInfo = Depends(JWTCookie(roles=[
            Role.user, Role.moderator
        ])),
        db_session: AsyncSession = Depends(get_session)
):
    if not report or report.status != ReportStatus.open:
        raise report_not_found_error
    comment = await ReportRepo.create_comment(
        report_id=report.id,
        sender_id=user_info.id,
        text=comment_data.text,
        db_session=db_session
    )
    await db_session.refresh(report)
    redis_client = RedisHandler().client
    comment_scheme = CommentOutScheme(
            text=comment.text,
            sender_id=str(comment.sender_id),
            sender_name=(await UserRepo.get_by_id(
                user_id=user_info.id,
                db_session=db_session
            )).name,
            created_at=comment.created_at
        )
    await redis_client.publish(
        f'comments_{str(report.article_id)}',
        comment_scheme.model_dump_json()
    )
    return DataResponse(
        data={
            'comment': comment_scheme
        }
    )
