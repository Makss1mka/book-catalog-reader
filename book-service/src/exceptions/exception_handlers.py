from src.models.enums import ResponseDataType, ResponseStatus
from src.exceptions.code_exceptions import CodeException
from src.models.response_dtos import CommonResponseModel

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

import logging

logger: logging.Logger = logging.getLogger(__name__)

async def code_exception_handler(req: Request, ex: CodeException):
    logger.debug(f"CODE EXCEPTION: {ex.status_code} | {ex.message}")

    return JSONResponse(
        status_code=ex.status_code,
        content=CommonResponseModel(
            status=ResponseStatus.EXCEPTION,
            data_type=ResponseDataType.STRING,
            data=ex.message,
        ).model_dump()
    )

async def pydantic_validation_exception_handler(req: Request, ex: RequestValidationError):
    logger.debug(f"VALIDATION EXCEPTION: {ex.errors} | {ex.__traceback__}")

    error_messages = ""
    isFirst = True
    for error in ex.errors():
        if isFirst:
            isFirst = False
        else:
            error_messages += "\n"
        error_message = error.get("msg")
        error_messages += error_message 
            

    return JSONResponse(
        status_code=400,
        content=CommonResponseModel(
            status=ResponseStatus.EXCEPTION,
            data_type=ResponseDataType.STRING,
            data=error_messages,
        ).model_dump()
    )

async def exception_handler(req: Request, ex: Exception):
    return JSONResponse(
        status_code=500,
        content=CommonResponseModel(
            status=ResponseStatus.EXCEPTION,
            data_type=ResponseDataType.STRING,
            data="Internal server error",
        ).model_dump()
    )
