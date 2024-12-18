import http
import traceback
from typing import Callable, Type

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.http_responses import Response500, http_responses
from src.logger import get_logger
from src.responses import (
    BaseResponse,
    DebugErrorResponse,
    ValidationErrorResponse,
)
from src.settings import LOGGER_PREFIX


type ExceptionHandler = Callable[[Request, Exception], Response]
logger = get_logger(LOGGER_PREFIX + '.exc')


def log_exception(
        request: Request, exc: Exception, response: Response
) -> None:
    """Logs exception details to the logger."""
    logger.exception(
        'Request exception: '
        '{client} - \033[1m {status} {method} {path} {query}\033[0m\n'
        'Error: {msg}'.format(
            client=request.scope.get('client'),
            status=response.status_code,
            method=request.scope.get('method'),
            path=request.scope.get('path'),
            query=request.scope.get('query_string', b"").decode(),
            msg=str(exc),
        ),
    )


async def debug_exception_handler(
        request: Request, exc: Exception
) -> JSONResponse:
    """Formats uncaught exception as 500 http response with debug info"""
    traceback_str = traceback.format_exc()
    response = DebugErrorResponse(
        message=f'Error: {str(exc)}',
        traceback_lines=traceback_str.split('\n'),
        traceback=traceback_str,
    )
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response.model_dump(mode='json'),
    )
    log_exception(request, exc, response)
    return response


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for all uncaught exceptions"""
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=Response500().model_dump(mode='json'),
    )
    log_exception(request, exc, response)
    return response


async def validation_exception_handler(
        request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Formats validation error to base response format.

    Args:
        request: The FastAPI request object.
        exc: The RequestValidationError exception object that was raised.

    Returns:
        JSONResponse with 422 response and validation errors data.
    """
    response = ValidationErrorResponse(errors=exc.errors())
    logger.error(response.model_dump_json())
    response = JSONResponse(
        status_code=http.HTTPStatus.UNPROCESSABLE_ENTITY,
        content=response.model_dump(mode='json'),
    )
    return response


async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handler for HTTPException responses which must be presented as JSON
    """
    response = http_responses.get(exc.status_code, Response500)()
    if exc.detail:
        response.message = str(exc.detail)
    logger.warning(response.model_dump_json())
    response = JSONResponse(
        status_code=exc.status_code,
        content=response.model_dump(mode='json'),
    )
    return response


def init_exc_handlers(
        app: FastAPI,
        debug: bool = False,
        exception_handler: ExceptionHandler = exception_handler,
        debug_exception_handler: ExceptionHandler = debug_exception_handler,
        http_exception_handler: ExceptionHandler = http_exception_handler,
        validation_error_handler: ExceptionHandler = (
            validation_exception_handler
        ),
) -> None:
    """Initialize exception handlers for the FastAPI application"""

    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    if debug:
        app.add_exception_handler(Exception, debug_exception_handler)
    else:
        app.add_exception_handler(Exception, exception_handler)


def init_responses(
        app: FastAPI,
        validation_response: Type[BaseResponse] = ValidationErrorResponse,
        internal_server_error_response: Type[BaseResponse] = Response500,
) -> None:
    """
    Declares responses for UNPROCESSABLE_ENTITY and INTERNAL SERVER ERROR
        responses
    """
    app.router.responses[http.HTTPStatus.UNPROCESSABLE_ENTITY] = (
        {'model': validation_response}
    )
    app.router.responses[http.HTTPStatus.INTERNAL_SERVER_ERROR] = (
        {'model': internal_server_error_response}
    )
