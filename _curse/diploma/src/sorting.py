from enum import StrEnum
from typing import Any, NamedTuple, Unpack

import sqlalchemy as sa
from fastapi import Query


type Model = Any


class SortOrderOptions(StrEnum):
    asc = 'asc'
    desc = 'desc'


class SortParams(NamedTuple):
    sort_by: StrEnum
    sort_order: SortOrderOptions


def get_sort_params(
        *sort_options: Unpack[tuple[str]],
        default: str | None = None,
) -> SortParams:
    """Dynamically creates a FastAPI dependency for sorting parameters.

    Args:
        *sort_options: A tuple of strs representing the allowed
            sorting fields.
        default: The default field to sort by. If not provided,
            the first option in `sort_options` is used.

    Returns:
        A FastAPI dependency that provides sorting parameters (`sort_by`
        and `sort_order`) through query parameters.
    """
    try:
        default = default or next(iter(sort_options))
    except StopIteration:
        default = None
    options_str = '_'.join(sort_options)
    options_dict = {op: op for op in sort_options}
    sort_options_enum = StrEnum(f'SortOptions_{options_str}', options_dict)

    def _get_sort_params(
            sort_by: sort_options_enum | None = Query(  # type: ignore
                default, description='Sort by field'
            ),
            sort_order: SortOrderOptions = Query(
                SortOrderOptions.desc, description='Sort order'
            ),
    ):
        return SortParams(sort_by=sort_by, sort_order=sort_order)
    return _get_sort_params


def sort(
    statement: sa.Select[Any],
    *,
    sorting: SortParams,
    model: Model | None = None,
) -> sa.Select[Any]:
    """Applies `ORDER BY` to query by sorting params, returns query.

    Args:
        statement: The SQLAlchemy `SELECT` statement to paginate.
        sorting: Sorting params.
        model: Model from statement, used to detect field from `sort_by`.

    Returns:
        Statement with applied sorting.

    Raises:
        ValueError: Unable to detect a model from statement. Must be at
            first position of the select statement.
        AttributeError: Detected model doesn't have a field from `sort_by`.

    Example:
        >>> sorting = SortParams(sort_by='name', sort_order='desc')
        >>> stmt = select(User)
        >>> stmt = sort(session, stmt, sorting=sorting)

    """
    sort_order = sa.desc
    if sorting.sort_order == SortOrderOptions.asc:
        sort_order = sa.asc
    sort_by = str(sorting.sort_by)

    if model is None:
        if statement.columns[0]._is_table:
            model = statement.columns[0].table
        else:
            raise ValueError(f'Invalid statement for sorting: {statement}')

    try:
        sort_field = getattr(model, sort_by)
    except AttributeError:
        raise AttributeError(f'Sorting model {model} missing {sort_by} field')

    return statement.order_by(sort_order(sort_field))
