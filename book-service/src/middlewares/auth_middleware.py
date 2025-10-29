from fastapi import Request, HTTPException
from typing import Optional

from fastapi.responses import JSONResponse
from src.exceptions.code_exceptions import BadRequestException
from starlette.middleware.base import BaseHTTPMiddleware
from src.models.enums import UserRole, UserStatus
import logging
import uuid

logger = logging.getLogger(__name__)


class UserContext:
    def __init__(
        self,
        user_id: Optional[uuid.UUID] = None,
        user_name: Optional[str] = None,
        user_role: UserRole = UserRole.GUEST,
        user_status: Optional[UserStatus] = None
    ):
        self.user_id = user_id
        self.user_name = user_name
        self.user_role = user_role
        self.user_status = user_status
    
    @property
    def is_authenticated(self) -> bool:
        return self.user_id is not None
    
    @property
    def is_admin(self) -> bool:
        return self.user_role == UserRole.ADMIN
    
    @property
    def is_active(self) -> bool:
        return self.user_status == UserStatus.ACTIVE


async def extract_user_context(request: Request) -> UserContext:
    user_id_str = request.headers.get("X-User-Id")
    user_name_str = request.headers.get("X-User-Name")
    user_role_str = request.headers.get("X-User-Role", UserRole.GUEST.value)
    user_status_str = request.headers.get("X-User-Status")
    
    try:
        user_role = UserRole(user_role_str)
    except ValueError:
        logger.warning(f"Invalid user role: {user_role_str}")
        raise BadRequestException(f"Invalid user role")
    
    user_status = None
    if user_status_str:
        try:
            user_status = UserStatus(user_status_str)
        except ValueError:
            logger.warning(f"Invalid user status: {user_status_str}")
            raise BadRequestException(f"Invalid user status")
    
    user_id = None
    if user_id_str:
        try:
            user_id = uuid.UUID(user_id_str)
        except ValueError:
            logger.exception(f"Invalid uuid format: {user_id_str}")
            raise BadRequestException(f"Invalid uuid format")

    return UserContext(
        user_id=user_id,
        user_name=user_name_str,
        user_role=user_role,
        user_status=user_status
    )


def get_user_context(request: Request) -> UserContext:
    if not hasattr(request.state, 'user_context'):
        raise HTTPException(status_code=500, detail="User context not found in request state")
    return request.state.user_context


class UserContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            user_context = await extract_user_context(request)
        except BadRequestException as e:
            return JSONResponse(status_code=400, content={
                "status": "Exception",
                "message": e.message
            })

        request.state.user_context = user_context

        response = await call_next(request)
        return response
