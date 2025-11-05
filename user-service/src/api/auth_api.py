from src.models.request_dtos import UserRegistrationDTO, UserAuthDTO
from src.middlewares.access_control import require_access
from src.models.response_dtos import UserResponseDTO
from src.services.auth_service import AuthService
from src.annotations import DatabaseSession, UserContext, RedisClient 
from src.globals import (
    USER_ID_HEADER_NAME, USER_NAME_HEADER_NAME, USER_ROLE_HEADER_NAME, USER_STATUS_HEADER_NAME, USER_BLOCKED_FOR_HEADER_NAME, 
    TOKEN_COOKIE_NAME, TOKEN_COOKIE_MAX_AGE, TOKEN_COOKIE_SECURE, TOKEN_COOKIE_HTTP_ONLY, TOKEN_COOKIE_SAME_SITE
)
from src.models.response_dtos import UserResponseDTO
from fastapi import APIRouter, Request, Response
from src.models.enums import UserRole, UserStatus
import logging

logger: logging.Logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/users", tags=["Auth"])


@auth_router.post("/register", response_model=UserResponseDTO)
@require_access(
    allowed_roles=[UserRole.GUEST],
    require_authentication=False
)
async def register_user(
    request: Request,
    response: Response,
    user_reg_dto: UserRegistrationDTO,
    db: DatabaseSession,
    user_context: UserContext,
    redis: RedisClient 
) -> UserResponseDTO:
    auth_service = AuthService(db, user_context)

    user, token, session_id = await auth_service.register_user(user_reg_dto, redis)

    response.set_cookie(
        TOKEN_COOKIE_NAME, 
        token, 
        max_age=TOKEN_COOKIE_MAX_AGE, 
        secure=TOKEN_COOKIE_SECURE, 
        httponly=TOKEN_COOKIE_HTTP_ONLY, 
        samesite=TOKEN_COOKIE_SAME_SITE
    )
    
    response.headers[USER_ID_HEADER_NAME] = str(user.id)
    response.headers[USER_NAME_HEADER_NAME] = user.username
    response.headers[USER_STATUS_HEADER_NAME] = user.status
    response.headers[USER_ROLE_HEADER_NAME] = user.role
    response.headers[USER_BLOCKED_FOR_HEADER_NAME] = str(user.blocked_for) if user.status == UserStatus.BLOCKED.value else "-1"

    logger.debug(response.headers)

    return UserResponseDTO.from_entity(user)


@auth_router.post("/auth", response_model=UserResponseDTO)
@require_access(
    allowed_roles=[UserRole.GUEST],
    require_authentication=False
)
async def auth_user(
    request: Request,
    response: Response,
    user_auth_dto: UserAuthDTO,
    db: DatabaseSession,
    user_context: UserContext,
    redis: RedisClient
) -> UserResponseDTO:
    auth_service = AuthService(db, user_context)

    user, token, session_id = await auth_service.auth_user(user_auth_dto, redis)

    response.set_cookie(
        TOKEN_COOKIE_NAME, 
        token, 
        max_age=TOKEN_COOKIE_MAX_AGE, 
        secure=TOKEN_COOKIE_SECURE, 
        httponly=TOKEN_COOKIE_HTTP_ONLY, 
        samesite=TOKEN_COOKIE_SAME_SITE
    )

    response.headers[USER_ID_HEADER_NAME] = str(user.id)
    response.headers[USER_NAME_HEADER_NAME] = user.username
    response.headers[USER_STATUS_HEADER_NAME] = user.status
    response.headers[USER_ROLE_HEADER_NAME] = user.role
    response.headers[USER_BLOCKED_FOR_HEADER_NAME] = str(user.blocked_for) if user.status == UserStatus.BLOCKED.value else "-1"

    return UserResponseDTO.from_entity(user)


@auth_router.post("/refresh", response_model=UserResponseDTO)
@require_access(
    allowed_roles=[UserRole.GUEST],
    require_authentication=False
)
async def auth_user_with_token(
    request: Request,
    response: Response,
    db: DatabaseSession,
    user_context: UserContext,
    redis: RedisClient
) -> UserResponseDTO:
    auth_service = AuthService(db, user_context)

    token = request.cookies.get("refresh_token", "")
    logger.debug(f"token {token}")

    user, new_token, session_id = await auth_service.auth_via_token(token, redis)

    response.set_cookie(
        TOKEN_COOKIE_NAME, 
        new_token, 
        max_age=TOKEN_COOKIE_MAX_AGE, 
        secure=TOKEN_COOKIE_SECURE, 
        httponly=TOKEN_COOKIE_HTTP_ONLY, 
        samesite=TOKEN_COOKIE_SAME_SITE
    )
    
    response.headers[USER_ID_HEADER_NAME] = str(user.id)
    response.headers[USER_NAME_HEADER_NAME] = user.username
    response.headers[USER_STATUS_HEADER_NAME] = user.status
    response.headers[USER_ROLE_HEADER_NAME] = user.role
    response.headers[USER_BLOCKED_FOR_HEADER_NAME] = str(user.blocked_for) if user.status == UserStatus.BLOCKED.value else "-1"

    return UserResponseDTO.from_entity(user)
