import uuid
from datetime import  datetime

from pydantic import Field

from src.database.models import ReportStatus
from src.responses import Scheme


class CreateReportScheme(Scheme):
    text: str = Field(min_length=1, max_length=1024)
    reason_id: int


class EditReportScheme(CreateReportScheme):
    pass


class ReportOutScheme(CreateReportScheme):
    article_id: uuid.UUID
    status: ReportStatus
    closed_by_user_id: uuid.UUID


class ReportReasonOutScheme(Scheme):
    id: int
    text: str


class CreateCommentScheme(Scheme):
    text: str = Field(min_length=1, max_length=100)


class CommentOutScheme(CreateCommentScheme):
    text: str
    sender_id: uuid.UUID
    created_at: datetime
