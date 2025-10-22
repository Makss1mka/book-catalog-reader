from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.annotations import DatabaseSession, UserContext
from src.models.crud_request_dtos import BookStatusUpdateDTO, AuthorProfileStatusUpdateDTO
from src.models.response_dtos import StatusUpdateResponseDTO
from src.models.enums import UserRole
from src.services.status_service import StatusService
from src.middlewares.access_control import require_access

logger = logging.getLogger(__name__)

status_router = APIRouter(prefix="/", tags=["Status Management"])


@status_router.put("/books/{book_id}/status", response_model=StatusUpdateResponseDTO)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def update_book_status(
    request: Request,
    book_id: str,
    status_data: BookStatusUpdateDTO,
    db: DatabaseSession,
    user_context: UserContext
):
    status_service = StatusService(db)
    return await status_service.update_book_status(book_id, status_data, user_context)


@status_router.put("/authors/{author_id}/status", response_model=StatusUpdateResponseDTO)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def update_author_profile_status(
    request: Request,
    author_id: str,
    status_data: AuthorProfileStatusUpdateDTO,
    db: DatabaseSession,
    user_context: UserContext
):
    status_service = StatusService(db)
    return await status_service.update_author_profile_status(author_id, status_data, user_context)
