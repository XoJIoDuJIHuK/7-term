import math
from collections.abc import Sequence
from typing import Annotated, Any, NamedTuple, Self

import sqlalchemy as sa
from fastapi import Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import _ColumnsClauseArgument


class PaginationParams(NamedTuple):
    page: int
    per_page: int


def get_pagination_params(
    page: int = Query(
        1,
        description="Current page number",
        ge=1,
        examples=[1],
    ),
    per_page: int = Query(
        10,
        description="Number of items to get on a page",
        ge=1,
        examples=[10],
    )
):
    return PaginationParams(page=page, per_page=per_page)


PaginationParamsQuery = Annotated[
    PaginationParams, Depends(get_pagination_params)
]
"""Pagination query parameters - `page`, `per_page`."""


class PaginationSchema(BaseModel):
    """Pagination data schema."""

    total_items: int = Field(
        ...,
        description="Total number of elements (must be positive)",
        ge=0,
        examples=[5],
    )
    page: int = Field(
        ...,
        description="Current page (must be at least 1)",
        ge=1,
        examples=[1],
    )
    per_page: int = Field(
        ...,
        description="Number of items per page (must be positive)",
        ge=1,
        examples=[1],
    )
    next_page: int | None = Field(
        None,
        description="Number of the next page (can be None)",
        examples=[2],
    )
    prev_page: int | None = Field(
        None,
        description="Number of the previous page (can be None)",
        examples=[None],
    )
    total_pages: int = Field(
        ...,
        description="Number of total pages (must be positive)",
        ge=0,
        examples=[5],
    )

    @classmethod
    def from_params(
            cls, params: PaginationParams, total: int
    ) -> Self:
        """Create instance from pagination params and total items count.

        Args:
            params: Pagination params.
            total: A total number of items available for the pagination.

        Returns:
            The schema instance with calculated fields.
        """
        is_last_page = params.page * params.per_page >= total
        return cls(
            total_items=total,
            page=params.page,
            per_page=params.per_page,
            next_page=params.page + 1 if not is_last_page else None,
            prev_page=params.page - 1 if params.page > 1 else None,
            total_pages=math.ceil(total / params.per_page),
        )


async def paginate(
    session: AsyncSession,
    statement: sa.Select[Any],
    *,
    pagination: PaginationParams,
    count_clause: _ColumnsClauseArgument[Any] | None = None,
) -> tuple[Sequence[Any], int]:
    """Paginates query by pagination params, returns result and total count.

    Args:
        session: The SQLAlchemy session.
        statement: The SQLAlchemy `SELECT` statement to paginate.
        pagination: Pagination params.
        count_clause: Custom count clause. If not provided, the total
            count will be calculated using the `COUNT() OVER ()`
            window function.

    Returns:
        - List selected items with applied pagination.
        - The total number of rows that match the query before pagination
            is applied.

    Example:
        # pagination = PaginationParams(page=2, limit=10)
        # stmt = select(User).where(User.is_active == True)
        # users, total = await paginate(session, stmt, pagination=pagination)

    """
    offset = pagination.per_page * (pagination.page - 1)
    statement = statement.offset(offset).limit(pagination.per_page)

    if count_clause is None:
        statement = statement.add_columns(sa.over(sa.func.count()))
    else:
        statement = statement.add_columns(count_clause)

    result = await session.execute(statement)

    rows: list[Any] = []
    count = 0
    for row in result.unique().all():
        (*queried_data, c) = row._tuple()
        count = int(c)
        if len(queried_data) == 1:
            rows.append(queried_data[0])
        else:
            rows.append(queried_data)

    return rows, count
