from src.utils.trace_id import add_trace_id, replace_trace_id
from src.services.session_service import SessionService
from src.exceptions.code_exceptions import NotFoundException, GatewayTimeoutException
from src.annotations import RedisClient
from src.globals import (
    SERVICES_URLS, STATIC_NGINX_URL, SERVICE_NOT_RESPONDING_TIMEOUT, ALLOWED_RETURNING_HEADERS,
    SESSION_COOKIE_NAME, SESSION_COOKIE_MAX_AGE, SESSION_COOKIE_HTTP_ONLY, SESSION_COOKIE_SAME_SITE, SESSION_COOKIE_SECURE
)

from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
from urllib.parse import urljoin
from multidict import MultiDict
import aiohttp
import asyncio
import logging
import json

main_router = APIRouter()

logger: logging.Logger = logging.getLogger("main_router")


@main_router.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUTCH", "DELETE", "PUT", "UPDATE", "OPTION"])
async def proxy_api(
    service: str, 
    path: str, 
    req: Request, 
    resp: Response,
    redis_client: RedisClient,
):
    if service not in SERVICES_URLS:
        raise NotFoundException("Cannot find such service!")

    req_headers_copy = dict(req.headers)
    add_trace_id(req_headers_copy)

    session_service = SessionService(redis_client, req, resp)
    await session_service.check_and_get_session_from_request(req_headers_copy)

    target_url = urljoin(SERVICES_URLS[service], path)
    logger.debug(f"Routing {target_url}")

    async with aiohttp.ClientSession() as session:
        session: aiohttp.ClientSession

        body = await req.body()
        
        try:
            async with session.request(
                method=req.method,
                url=target_url,
                headers=req_headers_copy,
                data=body,
                params=req.query_params,
                timeout=SERVICE_NOT_RESPONDING_TIMEOUT
            ) as response:
                returned_headers = MultiDict(response.headers)

                user_session_data = session_service.get_user_session(returned_headers)

                session_id = await session_service.add_session(user_session_data)

                replace_trace_id(returned_headers)

                for return_header_name, value in returned_headers.items():
                    if return_header_name.lower() in ALLOWED_RETURNING_HEADERS:
                        resp.headers[return_header_name] = value

                resp.set_cookie(
                    SESSION_COOKIE_NAME, 
                    session_id, 
                    max_age=SESSION_COOKIE_MAX_AGE, 
                    secure=SESSION_COOKIE_SECURE, 
                    httponly=SESSION_COOKIE_HTTP_ONLY, 
                    samesite=SESSION_COOKIE_SAME_SITE
                )
                resp.status_code = response.status
                
                if resp.headers["Content-Type"] == "application/json":
                    return json.loads(
                        await response.read()
                    )
                else:
                    return await response.read()
        except asyncio.TimeoutError:
            raise GatewayTimeoutException("Service is not responding")

@main_router.get("/static/{path:path}")
async def proxy_static(
    req: Request, 
    path: str
):
    target_url = urljoin(STATIC_NGINX_URL, path)

    async with aiohttp.ClientSession() as session:
        session: aiohttp.ClientSession

        async with session.get(target_url) as response:
            return StreamingResponse(
                content=response.content,
                status_code=response.status,
                headers=dict(response.headers),
            )
