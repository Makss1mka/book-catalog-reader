from src.utils.trace_id import add_trace_id, replace_trace_id
from src.exceptions.code_exceptions import GatewayTimeoutException, ForbiddenException
from src.annotations import ClientSession
from src.globals import (
    REGISTER_URL, REFRESH_URL, LOGIN_URL, AUTH_SERVICE_NAME, SERVICE_NOT_RESPONDING_TIMEOUT, ALLOWED_RETURNING_HEADERS,
    TOKEN_COOKIE_NAME, TOKEN_COOKIE_HTTP_ONLY, TOKEN_COOKIE_MAX_AGE, TOKEN_COOKIE_SAME_SITE, TOKEN_COOKIE_SECURE,
    SERVICES_URLS
)

from fastapi import APIRouter, Request, Response
from multidict import MultiDict
import aiohttp
import asyncio
import logging
import json

auth_router = APIRouter()
logger = logging.getLogger("auth_router")


async def _auth_proxy(
    req: Request,
    resp: Response,
    proxy_url: str,
    client_session: aiohttp.ClientSession,
):
    req_headers = dict(req.headers)
    add_trace_id(req_headers)

    target_url = SERVICES_URLS["user-service"] + "/users" + proxy_url
    logger.debug(f"Routing to {target_url}")

    try:
        async with client_session.request(
            method=req.method,
            url=target_url,
            headers=req_headers,
            data=await req.body(),
            params=req.query_params,
            timeout=SERVICE_NOT_RESPONDING_TIMEOUT
        ) as response:
            returned_headers = MultiDict(response.headers)
            response_data = await response.read()

            for header_name, value in returned_headers.items():
                if header_name.lower() in ALLOWED_RETURNING_HEADERS:
                    resp.headers[header_name] = value

            resp.status_code = response.status
            
            content_type = resp.headers.get("Content-Type", "").lower()

            replace_trace_id(returned_headers)

            logger.debug(resp.headers)
            logger.debug(response_data)

            if response.status == 200:
                response_data = json.loads(response_data)

                resp.set_cookie(
                    TOKEN_COOKIE_NAME, 
                    response_data["access_token"], 
                    max_age=TOKEN_COOKIE_MAX_AGE, 
                    secure=TOKEN_COOKIE_SECURE, 
                    httponly=TOKEN_COOKIE_HTTP_ONLY, 
                    samesite=TOKEN_COOKIE_SAME_SITE
                )
            elif "application/json" in content_type:
                response_data = json.loads(response_data)

            logger.debug(response_data)
            return response_data
    except asyncio.TimeoutError:
        raise GatewayTimeoutException("Service is not responding")

    except aiohttp.ClientError as e:
        raise ForbiddenException("Internal service error")




@auth_router.post("/api" + AUTH_SERVICE_NAME + REGISTER_URL)
async def register(req: Request, resp: Response, client_session: ClientSession):
    return await _auth_proxy(req, resp, REGISTER_URL, client_session)

@auth_router.post("/api" + AUTH_SERVICE_NAME + LOGIN_URL)
async def login(req: Request, resp: Response, client_session: ClientSession):
    return await _auth_proxy(req, resp, LOGIN_URL, client_session)

@auth_router.post("/api" + AUTH_SERVICE_NAME + REFRESH_URL)
async def refresh(req: Request, resp: Response, client_session: ClientSession):
    return await _auth_proxy(req, resp, REFRESH_URL, client_session)
