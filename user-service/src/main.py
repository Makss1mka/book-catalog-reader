from src.config.db_configs import DatabaseConfig, PoolConfig, ConnectionConfig
from src.api.users_cruds_api import user_crud_router
from src.api.auth_api import auth_router
from src.core.redis_core import redis_client_init
from src.core.logging_core import setup_logging
from src.core.db_core import init_engine
from src.exceptions.code_exceptions import CodeException
from src.exceptions.exception_handlers import (
    pydantic_validation_exception_handler,
    code_exception_handler,
)
from src.middlewares.auth_middleware import UserContextMiddleware
from src.globals import (
    APP_HOST, APP_PORT,
    LOGS_LEVEL, LOGS_FILENAME, LOGS_FORMAT,
    DB_HOST, DB_URL, DB_USER, DB_PASSWORD, DB_NAME, DB_ECHO_MODE,
    REDIS_PORT, REDIS_HOST
)

from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI, Request

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

    database_config = DatabaseConfig(
        db_url=DB_URL,
        db_username=DB_USER,
        db_password=DB_PASSWORD,
        db_host=DB_HOST,
        db_name=DB_NAME
    )
    pool_config = PoolConfig(
        echo=DB_ECHO_MODE,
        hide_parameters=not DB_ECHO_MODE
    )
    connection_config = ConnectionConfig()

    await init_engine(
        app=app,
        db_config=database_config,
        pool_config=pool_config,
        connection_config=connection_config
    )

    await redis_client_init(
        app=app,
        redis_host=REDIS_HOST,
        redis_port=REDIS_PORT
    )

    logger.info(f"Server is started on {APP_HOST}:{APP_PORT}")
    yield
    logger.error("Server shutdown...")


app = FastAPI(lifespan=app_lifespan)

app.add_middleware(UserContextMiddleware)

app.include_router(auth_router)
app.include_router(user_crud_router)

app.add_exception_handler(RequestValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(CodeException, code_exception_handler)

if __name__ == "__main__":
    uvicorn.run(app, host=APP_HOST, port=APP_PORT)
