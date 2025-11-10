from src.models.crud_request_dtos import UserBookStatusCreateDTO, UserBookReadingStatusEndPageUpdateDTO, UserBookStatusUpdateDTO
from src.services.user_book_status_service import UserBookStatusService
from src.models.response_dtos import UserBookStatusListResponseDTO
from src.annotations import CommonParams, DatabaseSession, UserContext
from src.middlewares.access_control import require_access
from src.services.likes_service import LikesService
from src.models.enums import UserBookStatusEnum, UserRole

from fastapi import APIRouter, Query, Request
import logging
import uuid

logger = logging.getLogger(__name__)
user_book_statuses_router = APIRouter(tags=["User Statuses Managment"])


@user_book_statuses_router.post("/books/{book_id}/user-status")
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
    return {"message": "Status added successfully"}




@user_book_statuses_router.put("/books/{book_id}/user-status/end-page")
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
    return {"message": "End page updated successfully"}


@user_book_statuses_router.put("/books/{book_id}/user-status")
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
    return {"message": "Status updated successfully"}




@user_book_statuses_router.delete("/books/{book_id}/user-status")
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
    return {"message": "Status updated successfully"}


@user_book_statuses_router.get("/books/user-status", response_model=UserBookStatusListResponseDTO)
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
    return await status_service.get_statused_books(status, pagination)


