from starlette.middleware.base import BaseHTTPMiddleware
from src.globals import TRACE_ID_HEADER_NAME
import logging

logger = logging.getLogger(__name__)

class AddTraceIdHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        response.headers[TRACE_ID_HEADER_NAME] = request.headers.get(TRACE_ID_HEADER_NAME, None)

        return response
