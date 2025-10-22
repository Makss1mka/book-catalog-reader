from src.exceptions.code_exceptions import CodeException

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

import logging

logger: logging.Logger = logging.getLogger(__name__)

async def code_exception_handler(req: Request, ex: CodeException):
    logger.exception(f"CODE EXCEPTION: {ex.status_code} | {ex.message}")

    return JSONResponse(
        status_code=ex.status_code,
        content={"error": ex.message},
    )

async def pydantic_validation_exception_handler(req: Request, ex: RequestValidationError):
    logger.exception(f"VALIDATION EXCEPTION: {ex.errors} | {ex.__traceback__}")

    return JSONResponse(
        status_code=404,
        content={"error": "Validation failed"},
    )
