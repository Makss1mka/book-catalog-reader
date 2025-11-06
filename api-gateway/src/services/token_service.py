from src.exceptions.code_exceptions import UnauthorizedException
from src.globals import (
    ACCESS_TOKEN_SECRET, TOKEN_COOKIE_NAME,
    USER_BLOCKED_FOR_HEADER_NAME, USER_ID_HEADER_NAME, USER_NAME_HEADER_NAME, USER_ROLE_HEADER_NAME, USER_STATUS_HEADER_NAME
)

from fastapi import Request, Response
import logging
import jwt

logger = logging.getLogger(__name__)

class TokenService:
    def __init__(self, req: Request, resp: Response):
        self._req = req
        self._resp = resp
    
    async def _decode_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Refresh token is invalid")
   
    async def add_user_context(self, headers: dict) -> None:
        token = self._req.cookies.get(TOKEN_COOKIE_NAME)
        user_data = self._decode_access_token(token)

        try:
            headers[USER_ID_HEADER_NAME] = user_data["sub"]
            headers[USER_NAME_HEADER_NAME] = user_data["name"]
            headers[USER_ROLE_HEADER_NAME] = user_data["role"]
            headers[USER_STATUS_HEADER_NAME] = user_data["status"]
            headers[USER_BLOCKED_FOR_HEADER_NAME] = str(user_data["blocked_for"])
        except Exception as e:
            logger.debug(f"Error while try to add user context. {e}")
            return UnauthorizedException("Invalid token data")

