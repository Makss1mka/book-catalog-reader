from src.models.crud_request_dtos import UserBookStatusCreateDTO, UserBookReadingStatusEndPageUpdateDTO, UserBookStatusUpdateDTO
from src.services.user_book_status_service import UserBookStatusService
from src.annotations import CommonParams, DatabaseSession, UserContext
from src.models.enums import ResponseDataType, ResponseStatus
from src.models.enums import UserBookStatusEnum, UserRole
from src.middlewares.access_control import require_access
from src.models.response_dtos import CommonResponseModel

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Query, Request
import logging
import uuid

logger = logging.getLogger(__name__)
user_book_statuses_router = APIRouter(tags=["User Statuses Managment"])


@user_book_statuses_router.post("/books/{book_id}/user-status", response_class=JSONResponse, status_code=201)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def add_user_book_status(
    request: Request,
    book_id: uuid.UUID,
    create_status_dto: UserBookStatusCreateDTO, 
    db: DatabaseSession,
    user_context: UserContext
):
    status_service = UserBookStatusService(db, user_context)
    await status_service.add_status(book_id, create_status_dto)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.STRING,
        data="Status added successfully"
    )



@user_book_statuses_router.put("/books/{book_id}/user-status/end-page", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def update_end_page_status(
    request: Request,
    book_id: uuid.UUID,
    update_end_page_dto: UserBookReadingStatusEndPageUpdateDTO, 
    db: DatabaseSession,
    user_context: UserContext
):
    status_service = UserBookStatusService(db, user_context)
    await status_service.update_end_page(book_id, update_end_page_dto)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.STRING,
        data="End page updated successfully"
    )


@user_book_statuses_router.put("/books/{book_id}/user-status", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def update_user_book_status(
    request: Request,
    book_id: uuid.UUID,
    update_status_dto: UserBookStatusUpdateDTO, 
    db: DatabaseSession,
    user_context: UserContext
):
    status_service = UserBookStatusService(db, user_context)
    await status_service.update_status(book_id, update_status_dto)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.STRING,
        data="Status updated successfully"
    )


@user_book_statuses_router.delete("/books/{book_id}/user-status", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def delete_status(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    status_service = UserBookStatusService(db, user_context)
    await status_service.delete_status(book_id)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.STRING,
        data="Status deleted successfully"
    )


@user_book_statuses_router.get("/books/user-status", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def get_statused_books(
    request: Request,
    pagination: CommonParams,
    db: DatabaseSession,
    user_context: UserContext,
    status: UserBookStatusEnum = Query(None),
):
    status_service = UserBookStatusService(db, user_context)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await status_service.get_statused_books(status, pagination)
    )

