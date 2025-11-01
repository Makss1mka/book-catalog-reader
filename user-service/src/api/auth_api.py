from src.models.request_dtos import UserRegistrationDTO, UserAuthDTO
from src.middlewares.access_control import require_access
from src.models.response_dtos import UserResponseDTO
from src.services.auth_service import AuthService
from src.annotations import DatabaseSession, UserContext, RedisClient 
from fastapi import APIRouter, Request, Response
from src.models.enums import UserRole
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

    response.set_cookie("refresh_token", token)
    response.set_cookie("session_id", session_id)

    return user


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

    response.set_cookie("refresh_token", token)
    response.set_cookie("session_id", session_id)

    return user


@auth_router.post("/auth_with_token", response_model=UserResponseDTO)
@require_access(
    allowed_roles=[UserRole.GUEST],
    require_authentication=False
)
async def auth_user(
    request: Request,
    response: Response,
    user_authdto: UserAuthDTO,
    db: DatabaseSession,
    user_context: UserContext,
    redis: RedisClient
) -> UserResponseDTO:
    auth_service = AuthService(db, user_context)

    token = request.cookies.get("refresh_token", "")

    user, new_token, session_id = await auth_service.auth_via_token(token, redis)

    response.set_cookie("refresh_token", new_token)
    response.set_cookie("session_id", session_id)

    return user
