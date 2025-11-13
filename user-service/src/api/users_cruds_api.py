from src.models.enums import ResponseDataType, ResponseStatus
from src.models.response_dtos import CommonResponseModel
from src.models.request_dtos import UserUpdateDTO
from src.models.enums import UserRole
from src.middlewares.access_control import require_access
from src.annotations import UserContext
from src.services.user_service import UserService
from src.annotations import DatabaseSession
from fastapi.responses import JSONResponse

from fastapi import APIRouter, Request
import uuid


import logging

logger: logging.Logger = logging.getLogger(__name__)

user_crud_router = APIRouter(prefix="/users", tags=["User CREDS"])


@user_crud_router.get("/{user_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True,
    resource_owner_check=True
)
async def get_user_by_id(
    request: Request,
    user_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    user_service = UserService(db, user_context)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await user_service.get_user_by_id(user_id),
    )


@user_crud_router.put("/{user_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True,
    resource_owner_check=True
)
async def update_user(
    request: Request,
    user_id: uuid.UUID,
    update_user_dto: UserUpdateDTO,
    db: DatabaseSession,
    user_context: UserContext
):
    user_service = UserService(db, user_context)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await user_service.update_user(user_id, update_user_dto),
    )


@user_crud_router.delete("/{user_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True,
    resource_owner_check=True
)
async def delete_user(
    request: Request,
    user_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    user_service = UserService(db, user_context)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.STRING,
        data=await user_service.delete_user(user_id),
    )
