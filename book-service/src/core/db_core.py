from src.config.db_configs import DatabaseConfig, PoolConfig, ConnectionConfig

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi import Request, FastAPI
from typing import AsyncGenerator
from sqlalchemy import text

import logging

logger: logging.Logger = logging.getLogger(__name__)

async def init_engine(
    app: FastAPI,
    db_config: DatabaseConfig,
    pool_config: PoolConfig,
    connection_config: ConnectionConfig
) -> None:
    logger.info(f"Initializing database engine")

    if (
        not db_config.db_url
        or not db_config.db_username
        or not db_config.db_password
        or not db_config.db_host
        or not db_config.db_name
    ):
        raise ValueError("Invalid database configuration")

    connection_url = db_config.db_url.format(
        username=db_config.db_username,
        password=db_config.db_password,
        host=db_config.db_host,
        bd_name=db_config.db_name
    )

    app.state.db_engine = create_async_engine(
        connection_url,
        pool_size=pool_config.pool_size,
        max_overflow=pool_config.max_overflows,
        pool_timeout=pool_config.pool_timeout,
        pool_recycle=pool_config.pool_recycle,
        pool_pre_ping=pool_config.pool_pre_ping,
        echo=pool_config.echo,
        echo_pool=pool_config.echo_pool,
        hide_parameters=pool_config.hide_parameters
    )

    app.state.db_session_maker = sessionmaker(
        app.state.db_engine,
        class_=AsyncSession
    )

    logger.info(f"Database engine initialized")

    # Check if the database is reachable
    logger.debug(f"Checking if the database is reachable")
    try:
        async with app.state.db_session_maker() as session:
            res = await session.execute(text("SELECT 1"))
            logger.debug(f"Database is reachable")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        raise Exception("Failed to connect to the database") from e
    logger.info("Database is initialized")


async def get_db_session(req: Request) -> AsyncGenerator[AsyncSession, None]:
    async with req.app.state.db_session_maker() as session:
        yield session

