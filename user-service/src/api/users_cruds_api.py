from src.models.entities import User
from src.models.response_dtos import UserResponseDTO, UserProfileResponseDTO
from src.models.request_dtos import UserUpdateDTO
from src.models.enums import UserRole, UserStatus
from src.middlewares.access_control import require_access
from src.middlewares.auth_middleware import UserContext
from src.services.user_service import UserService
from src.annotations import DatabaseSession

from fastapi import APIRouter, Request, Response, Path
from uuid import UUID

import logging

logger: logging.Logger = logging.getLogger(__name__)

users_crud_router = APIRouter(prefix="/users", tags=["User CREDS"])


@users_crud_router.get("/{user_id}/profile")
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True,
    resource_owner_check=True
)
async def get_user_by_id(
    request: Request,
    user_id: UUID,
    db: DatabaseSession,
    user_context: UserContext
) -> UserProfileResponseDTO:
    user_service = UserService(db, user_context)
    return await user_service.get_user_by_id(user_id)


@users_crud_router.put("/{user_id}")
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True,
    resource_owner_check=True
)
async def update_user(
    request: Request,
    user_id: UUID,
    update_user_dto: UserUpdateDTO,
    db: DatabaseSession,
    user_context: UserContext
) -> UserProfileResponseDTO:
    user_service = UserService(db, user_context)
    return await user_service.get_user_by_id(user_id, update_user_dto)


@users_crud_router.delete("/{user_id}")
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True,
    resource_owner_check=True
)
async def delete_user(
    request: Request,
    user_create_dto: UserCreateDTO,
    db: DatabaseSession,
    user_context: UserContext
) -> dict:
    user_service = UserService(db, user_context)
    message = await user_service.get_user_by_id(user_id, update_user_dto)

    return {
        "status": "OK",
        "message": message
    }



