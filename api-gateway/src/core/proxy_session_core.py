from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, Request
import aiohttp
import logging

logger: logging.Logger = logging.getLogger(__name__)

@asynccontextmanager
async def proxy_client_session_init(app: FastAPI) -> None:
    async with aiohttp.ClientSession() as session:
        app.state.proxy_client_session = session

        logger.info("Proxy client session created")
        yield
    logger.info("Proxy client session closed")

async def get_proxy_client_session(req: Request) -> AsyncGenerator[aiohttp.ClientSession, None]:
    yield req.app.state.proxy_client_session
   

