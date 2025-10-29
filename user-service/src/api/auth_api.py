from src.models.response_dtos import UserResponseDTO, UserProfileResponseDTO
from src.models.request_dtos import UserRegistrationDTO, UserAuthDTO
from src.models.enums import UserRole, UserStatus
from src.middlewares.access_control import require_access
from src.middlewares.auth_middleware import UserContext
from src.services.auth_service import AuthService
from src.annotations import DatabaseSession

from fastapi import APIRouter, Request, Response, Path
from uuid import UUID

import logging

logger: logging.Logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/users", tags=["Auth"])


@auth_router.post("/register")
@require_access(
    allowed_roles=[UserRole.GUEST],
    require_authentication=False
)
async def register_user(
    request: Request,
    user_reg_dto: UserRegistrationDTO,
    db: DatabaseSession,
    user_context: UserContext
) -> UserResponseDTO:
    auth_service = AuthService(db, user_context)
    return await auth_service.register_user(user_reg_dto)


@auth_router.post("/auth")
@require_access(
    allowed_roles=[UserRole.GUEST],
    require_authentication=False
)
async def auth_user(
    request: Request,
    user_authdto: UserAuthDTO,
    db: DatabaseSession,
    user_context: UserContext
) -> UserResponseDTO:
    auth_service = AuthService(db, user_context)
    return await auth_service.auth_user(user_authdto)
