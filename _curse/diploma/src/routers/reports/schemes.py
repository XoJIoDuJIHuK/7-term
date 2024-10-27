import uuid
from datetime import  datetime

from pydantic import Field

from src.database.models import ReportStatus, Report
from src.responses import Scheme
from src.settings import Role


class FilterReportsScheme(Scheme):
    status: ReportStatus | None = None
    user_id: uuid.UUID | None = None
    article_id: uuid.UUID | None = None


class CreateReportScheme(Scheme):
    text: str = Field(min_length=1, max_length=1024)
    reason_id: int


class EditReportScheme(CreateReportScheme):
    pass


class ReportListItemScheme(Scheme):
    article_id: uuid.UUID
    status: ReportStatus
    reason_text: str
    closed_at: datetime | None = None
    closed_by_user_name: str | None = None

    @classmethod
    def create(cls, report_object: Report):
        closed_by_user = report_object.closed_by_user
        closed_by_user_name = closed_by_user.name if closed_by_user else None
        return cls(
            article_id=report_object.article_id,
            status=report_object.status,
            closed_at=report_object.closed_at,
            closed_by_user_name=closed_by_user_name,
            reason_text = report_object.reason.text,
        )


class ReportOutScheme(ReportListItemScheme):
    text: str = Field(min_length=1, max_length=1024)

    @classmethod
    def create(cls, report_object: Report):
        closed_by_user = report_object.closed_by_user
        closed_by_user_name = closed_by_user.name if closed_by_user else None
        return cls(
            text=report_object.text,
            article_id=report_object.article_id,
            status=report_object.status,
            closed_at=report_object.closed_at,
            closed_by_user_name=closed_by_user_name,
            reason_text=report_object.reason.text,
        )


class ReportReasonOutScheme(Scheme):
    id: int
    text: str


class CreateCommentScheme(Scheme):
    text: str = Field(min_length=1, max_length=100)


class CommentOutScheme(CreateCommentScheme):
    text: str
    sender_id: uuid.UUID
    sender_name: str
    created_at: datetime
