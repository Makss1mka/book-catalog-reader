from src.globals import SERVICES_URLS, STATIC_NGINX_URL, SERVICE_NOT_RESPONDING_TIMEOUT, ALLOWED_RETURNING_HEADERS
from src.exceptions.code_exceptions import NotFoundException, GatewayTimeoutException
from src.utils.trace_id import add_trace_id, replace_trace_id
from src.services.token_service import TokenService
from src.annotations import ClientSession

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from urllib.parse import urljoin
from multidict import MultiDict
import aiohttp
import asyncio
import logging
import json

main_router = APIRouter()
logger = logging.getLogger("main_router")


async def _stream_from_aiohttp(response: aiohttp.ClientResponse):
    try:
        async for chunk in response.content.iter_chunked(1024 * 64):
            yield chunk
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        raise
    finally:
        response.close()


@main_router.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_api(
    service: str,
    path: str,
    req: Request,
    resp: Response,
    client_session: ClientSession
):
    if service not in SERVICES_URLS:
        raise NotFoundException("Cannot find such service!")

    token_service = TokenService(req, resp)
    req_headers = dict(req.headers)
    add_trace_id(req_headers)
    token_service.add_user_context(req_headers)

    target_url = urljoin(SERVICES_URLS[service], path)
    logger.debug(f"Routing to {target_url}")

    body = await req.body()

    response = await client_session.request(
        method=req.method,
        url=target_url,
        headers=req_headers,
        data=body,
        params=req.query_params,
        timeout=SERVICE_NOT_RESPONDING_TIMEOUT
    )

    try:
        returned_headers = MultiDict(response.headers)
        replace_trace_id(returned_headers)

        for header_name, value in returned_headers.items():
            if header_name.lower() in ALLOWED_RETURNING_HEADERS:
                resp.headers[header_name] = value

        content_type = resp.headers.get("Content-Type", "").lower()

        if "application/json" in content_type:
            content = await response.read()
            try:
                json_data = json.loads(content)
                await response.release()
                return json_data
            except json.JSONDecodeError as e:
                await response.release()
                logger.error(f"Invalid JSON from {target_url}: {e}")
                raise HTTPException(502, "Invalid JSON from service")

        else:
            async def _final_stream():
                try:
                    async for chunk in response.content.iter_chunked(1024 * 64):
                        yield chunk
                except Exception as e:
                    logger.error(f"Streaming error: {e}")
                    raise
                finally:
                    await response.release()

            return StreamingResponse(
                content=_final_stream(),
                status_code=response.status,
                headers=dict(resp.headers),
                media_type=content_type.split(";")[0] or "application/octet-stream"
            )

    except asyncio.TimeoutError:
        await response.release()
        logger.error(f"Timeout for {target_url}")
        raise GatewayTimeoutException("Service is not responding")
    except aiohttp.ClientError as e:
        await response.release()
        logger.error(f"Client error for {target_url}: {e}")
        raise HTTPException(502, "Bad gateway")
    except Exception as e:
        await response.release()
        logger.error(f"Unexpected error in proxy to {target_url}: {e}")
        raise HTTPException(500, "Internal proxy error")


@main_router.get("/static/{path:path}")
async def proxy_static(
    path: str,
    client_session: ClientSession
):
    target_url = urljoin(STATIC_NGINX_URL, path)

    async with client_session.get(target_url) as response:
        return StreamingResponse(
            content=response.content,
            status_code=response.status,
            headers=dict(response.headers),
        )
