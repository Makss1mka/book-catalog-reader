from src.api.main_proxy_api import main_router
from src.api.auth_api import auth_router
from src.core.logging_core import setup_logging
from src.core.proxy_session_core import proxy_client_session_init
from src.exceptions.code_exceptions import CodeException
from src.exceptions.exception_handlers import (
    pydantic_validation_exception_handler,
    code_exception_handler,
)
from src.globals import APP_HOST, APP_PORT, LOGS_LEVEL, LOGS_FILENAME, LOGS_FORMAT

from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI

import uvicorn
import logging


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging(
        logs_filename=LOGS_FILENAME,
        logs_format=LOGS_FORMAT,
        logs_level=LOGS_LEVEL,
    )

    logger: logging.Logger = logging.getLogger(__name__)

    async with (
        proxy_client_session_init(app)
    ):
        logger.info(f"Server is started on {APP_HOST}:{APP_PORT}")
        yield
        logger.error("Server shutdown...")


app = FastAPI(lifespan=app_lifespan)

app.include_router(auth_router)
app.include_router(main_router)

app.add_exception_handler(RequestValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(CodeException, code_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
