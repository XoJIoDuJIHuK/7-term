from http import HTTPStatus
from typing import Final, Unpack

from pydantic import Field, create_model

from src.responses import BaseResponse


type StatusCode = int


def _create_response_model(status: HTTPStatus) -> BaseResponse:
    return create_model(
        f'Response{status._value_}',
        __base__=BaseResponse,
        __doc__=(
            f"""{status._value_} status response schema.

            {status.phrase} - {status.description}
            """
        ),
        success=(bool, Field(default=status.is_success)),
        message=(str, Field(default=status.phrase)),
    )


class Response200(BaseResponse):
    success: bool = HTTPStatus.OK.is_success
    message: str = HTTPStatus.OK.phrase


class Response201(BaseResponse):
    success: bool = HTTPStatus.CREATED.is_success
    message: str = HTTPStatus.CREATED.phrase


# Informational responses
Response101 = _create_response_model(HTTPStatus.SWITCHING_PROTOCOLS)

# Successful responses
Response202 = _create_response_model(HTTPStatus.ACCEPTED)

Response400 = _create_response_model(HTTPStatus.BAD_REQUEST)
Response401 = _create_response_model(HTTPStatus.UNAUTHORIZED)
Response403 = _create_response_model(HTTPStatus.FORBIDDEN)
Response404 = _create_response_model(HTTPStatus.NOT_FOUND)
Response409 = _create_response_model(HTTPStatus.CONFLICT)
Response413 = _create_response_model(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
Response415 = _create_response_model(HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
Response418 = _create_response_model(HTTPStatus.IM_A_TEAPOT)
Response422 = _create_response_model(HTTPStatus.UNPROCESSABLE_ENTITY)
Response429 = _create_response_model(HTTPStatus.TOO_MANY_REQUESTS)

# Server error responses
Response500 = _create_response_model(HTTPStatus.INTERNAL_SERVER_ERROR)
Response501 = _create_response_model(HTTPStatus.NOT_IMPLEMENTED)
Response503 = _create_response_model(HTTPStatus.SERVICE_UNAVAILABLE)


def _gather_http_responses() -> dict[StatusCode, BaseResponse]:
    responses = {}

    response_prefix = 'Response'
    for var_name, var_value in globals().items():
        if var_name.startswith(response_prefix):

            postfix = var_name[len(response_prefix):]
            if not postfix.isdigit() or len(postfix) != 3:
                continue

            code = int(postfix)
            responses[code] = var_value
    return responses


http_responses: Final = _gather_http_responses()


def get_responses(
        *codes: Unpack[tuple[StatusCode]]
) -> dict[StatusCode, dict[str, BaseResponse]]:
    """Creates responses dictionary for endpoint Swagger"""
    responses = {}
    for code in sorted(codes):
        response = http_responses.get(code, BaseResponse)
        responses[code] = {'model': response}
    return responses
