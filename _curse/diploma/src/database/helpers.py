from typing import Type

from sqlalchemy import and_

from src.database import Base
from src.responses import Scheme


def build_where_clause(filter_params: Scheme, model: Type[Base]):
    """
    Builds a SQLAlchemy WHERE clause from filter parameters

    Example:
        >>> from sqlalchemy import select
        >>> from src.database.models import User
        >>> from src.routers.reports.schemes import FilterReportsScheme
        >>> some_filter_params = FilterReportsScheme(user_id='234567890765432')
        >>> query = select(User)
        >>> where_clause = build_where_clause(some_filter_params, User)
        >>> if where_clause:
        >>>     query = query.where(where_clause)
    """
    where_clauses = []
    print(filter_params.model_dump().items())
    for field_name, value in filter_params.model_dump().items():
        if value is not None:
            field_object = getattr(model, field_name)
            where_clauses.append(field_object == value)
    if len(where_clauses) == 0:
        return None
    elif len(where_clauses) == 1:
        return where_clauses[0]
    return and_(*where_clauses)


def update_model_by_scheme(
        model: Base,
        scheme: Scheme
):
    for field_name, value in scheme.model_dump(exclude_unset=True).items():
        setattr(model, field_name, value)
    return model
