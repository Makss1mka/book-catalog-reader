from src.globals import (
    USER_ID_HEADER_NAME, USER_NAME_HEADER_NAME, USER_ROLE_HEADER_NAME, 
    USER_STATUS_HEADER_NAME, USER_BLOCKED_FOR_HEADER_NAME, TRACE_ID_HEADER_NAME
)
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class AddUserSessionHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        should_copy = True if USER_ID_HEADER_NAME in request.headers else False

        response = await call_next(request)
        
        if should_copy:
            response.headers[USER_ID_HEADER_NAME] = request.headers.get(USER_ID_HEADER_NAME, None)
            response.headers[USER_NAME_HEADER_NAME] = request.headers.get(USER_NAME_HEADER_NAME, None)
            response.headers[USER_STATUS_HEADER_NAME] = request.headers.get(USER_STATUS_HEADER_NAME, None)
            response.headers[USER_ROLE_HEADER_NAME] = request.headers.get(USER_ROLE_HEADER_NAME, None)
            response.headers[USER_BLOCKED_FOR_HEADER_NAME] = request.headers.get(USER_BLOCKED_FOR_HEADER_NAME, None)
        
        return response

class AddTraceIdHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        response.headers[TRACE_ID_HEADER_NAME] = request.headers.get(TRACE_ID_HEADER_NAME, None)

        return response