from src.models.response_dtos import CommonResponseModel
from src.models.enums import ResponseDataType, ResponseStatus
from src.models.crud_request_dtos import AuthorProfileCreateDTO, AuthorProfileUpdateDTO
from src.annotations import DatabaseSession, UserContext
from src.models.response_dtos import AuthorProfileResponseDTO
from src.models.enums import UserRole
from src.services.author_service import AuthorProfileService
from src.middlewares.access_control import require_access

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
from typing import List
import logging
import uuid

logger = logging.getLogger(__name__)

author_crud_router = APIRouter(prefix="/authors", tags=["Authors CRUD"])


@author_crud_router.post("/", response_class=JSONResponse, status_code=201)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def create_author_profile(
    request: Request,
    author_data: AuthorProfileCreateDTO,
    db: DatabaseSession,
    user_context: UserContext
):
    author_service = AuthorProfileService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await author_service.create_author_profile(author_data, user_context.user_id)
    )


@author_crud_router.get("/", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.GUEST, UserRole.USER, UserRole.ADMIN],
    require_authentication=False
)
async def get_all_author_profiles(
    request: Request,
    db: DatabaseSession,
    user_context: UserContext
):
    author_service = AuthorProfileService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await author_service.get_all_author_profiles(user_context, include_books=False)
    )


@author_crud_router.get("/{author_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.GUEST, UserRole.USER, UserRole.ADMIN],
    require_authentication=False
)
async def get_author_profile(
    request: Request,
    author_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    author_service = AuthorProfileService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await author_service.get_author_profile_by_id(author_id, user_context, include_books=True)
    )


@author_crud_router.put("/{author_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def update_author_profile(
    request: Request,
    author_id: uuid.UUID,
    author_data: AuthorProfileUpdateDTO,
    db: DatabaseSession,
    user_context: UserContext
):
    author_service = AuthorProfileService(db)
    
    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await author_service.update_author_profile(author_id, author_data, user_context)
    )


@author_crud_router.delete("/{author_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def delete_author_profile(
    request: Request,
    author_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    author_service = AuthorProfileService(db)
    await author_service.delete_author_profile(author_id, user_context)
    
    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.STRING,
        data="Author profile deleted successfully"
    )
