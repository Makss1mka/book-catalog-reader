from src.models.crud_request_dtos import BookStatusUpdateDTO, AuthorProfileStatusUpdateDTO
from src.models.enums import ResponseDataType, ResponseStatus
from src.services.system_status_service import StatusService
from src.middlewares.access_control import require_access
from src.models.response_dtos import CommonResponseModel
from src.annotations import DatabaseSession, UserContext
from src.models.enums import UserRole

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
import logging
import uuid


logger = logging.getLogger(__name__)

status_router = APIRouter(tags=["Status Management"])


@status_router.put("/books/{book_id}/system-status", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def update_book_status(
    request: Request,
    book_id: uuid.UUID,
    status_data: BookStatusUpdateDTO,
    db: DatabaseSession,
    user_context: UserContext
):
    status_service = StatusService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await status_service.update_book_status(book_id, status_data, user_context)
    )


@status_router.put("/authors/{author_id}/system-status", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def update_author_profile_status(
    request: Request,
    author_id: uuid.UUID,
    status_data: AuthorProfileStatusUpdateDTO,
    db: DatabaseSession,
    user_context: UserContext
):
    status_service = StatusService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await status_service.update_author_profile_status(author_id, status_data, user_context)
    )
