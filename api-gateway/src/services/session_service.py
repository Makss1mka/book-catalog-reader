from src.exceptions.code_exceptions import UnauthorizedException, ForbiddenException
from src.models.cache_models import UserSession
from src.models.enums import UserRole, UserStatus
from src.globals import (
    AUTH_FREE_PATHS, SESSION_COOKIE_NAME, SESSION_CACHE_TTL,
    USER_ID_HEADER_NAME, USER_ROLE_HEADER_NAME, USER_NAME_HEADER_NAME, USER_STATUS_HEADER_NAME, USER_BLOCKED_FOR_HEADER_NAME,
)

from redis.asyncio import Redis
from fastapi import Request, Response
import logging
import json
import uuid

logger: logging.Logger = logging.getLogger(__name__)


class SessionService:
    def __init__(
        self, 
        redis_client: Redis,
        req: Request,
        resp: Response
    ):
        self._redis_client: Redis = redis_client
        self._req = req
        self._resp = resp
    
    async def get_session(
        self, 
        session_id: str
    ) -> UserSession | None:
        session_data = await self._redis_client.get(session_id)

        if session_data == None:
            return None
            
        return UserSession.from_json(session_data)

    async def add_session(
        self,
        session_data: UserSession
    ) -> None | str:
        if not UserSession: return

        session_id = str(uuid.uuid4())
        
        await self._redis_client.set(session_id, session_data.to_json(), SESSION_CACHE_TTL)

        return session_id

    async def delete_session(
        self,
        session_id: str
    ) -> None:
        await self._redis_client.delete(session_id)

    async def check_and_get_session_from_request(
        self,
        req_headers: dict,
    ) -> None:
        session_id = self._req.cookies.get(SESSION_COOKIE_NAME, None)
        
        if not session_id:
            req_headers[USER_ROLE_HEADER_NAME] = UserRole.GUEST.value
        else:
            session = await self.get_session(session_id)
            logger.debug(session_id)
            if not session:
                raise ForbiddenException("Session id is invalid!")
            
            req_headers[USER_ID_HEADER_NAME] = session.user_id
            req_headers[USER_ROLE_HEADER_NAME] = session.user_role
            req_headers[USER_STATUS_HEADER_NAME] = session.user_status
            req_headers[USER_NAME_HEADER_NAME] = session.user_name
            req_headers[USER_BLOCKED_FOR_HEADER_NAME] = session.user_blocked_for

    def get_user_session(
        self,
        headers: dict,
    ) -> UserSession | None:
        user_id = headers.get(USER_ID_HEADER_NAME, None)
        user_role = headers.get(USER_ROLE_HEADER_NAME, None)
        user_status = headers.get(USER_STATUS_HEADER_NAME, None)
        user_name = headers.get(USER_NAME_HEADER_NAME, None)
        user_blocked_for = headers.get(USER_BLOCKED_FOR_HEADER_NAME, None)

        if (
            not user_id 
            or not user_role
            or not user_status
            or not user_name
            or not user_blocked_for
        ):
            return None

        return UserSession(
            user_id=user_id,
            user_name=user_name,
            user_role=user_role,
            user_status=user_status,
            user_blocked_for=user_blocked_for
        )

