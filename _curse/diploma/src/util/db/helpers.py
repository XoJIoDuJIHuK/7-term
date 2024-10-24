from src.database import Base
from src.responses import Scheme


def update_object(
        db_object: Base,
        update_scheme: Scheme,
        skip_none_values: bool = True
):
    """Updates database model object with new values from the scheme

    :param db_object: the object to be updated
    :param update_scheme: pydantic scheme to take new values from
    :param skip_none_values: defines to skip properties which values are None
        or set respective db_object properties to None
    :return: db_object
    """
    for key, value in vars(update_scheme).items():
        if not skip_none_values or  skip_none_values and value is not None:
            db_object.__setattr__(key, value)
    return db_object
