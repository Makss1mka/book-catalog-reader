from fastapi import APIRouter, Depends, Request, Query, Response, UploadFile, File
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.annotations import DatabaseSession, UserContext
from src.models.response_dtos import BookPagesResponseDTO, BookPageResponseDTO, BookResponseDTO
from src.models.enums import BookStatus, UserRole
from src.services.book_file_service import BookFileService
from src.middlewares.access_control import require_access

logger = logging.getLogger(__name__)

book_file_router = APIRouter(prefix="/books", tags=["Book Files"])



@book_file_router.post("/{book_id}/content", response_model=BookResponseDTO)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    allowed_statuses=[BookStatus.WAIT_FILE, BookStatus.ON_MODERATE, BookStatus.PRIVATE, BookStatus.ON_APILATION, BookStatus.ACTIVE],
    require_authentication=True
)
async def add_book_content_file(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext,
    file: UploadFile = File(...),
) -> BookResponseDTO:
    book_file_service = BookFileService(db)
    return await book_file_service.set_content_file(book_id, file, user_context)


@book_file_router.post("/{book_id}/cover", response_model=BookResponseDTO)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def add_book_cover_file(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext,
    file: UploadFile = File(...)
) -> BookResponseDTO:
    book_file_service = BookFileService(db)
    return await book_file_service.set_cover_file(book_id, file, user_context)





@book_file_router.get("/{book_id}/pages")
@require_access(
    allowed_roles=[UserRole.GUEST, UserRole.USER, UserRole.ADMIN],
    require_authentication=False
)
async def get_book_pages(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext,
    start_page: int = Query(..., ge=1),
    end_page: int = Query(..., ge=1)
):
    book_file_service = BookFileService(db)
    file_content = await book_file_service.get_book_pages(book_id, start_page, end_page, user_context)

    return Response(
        content=file_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=book_{book_id}.pdf"}
    )


@book_file_router.get("/{book_id}/page/{page_number}")
@require_access(
    allowed_roles=[UserRole.GUEST, UserRole.USER, UserRole.ADMIN],
    require_authentication=False
)
async def get_book_page(
    request: Request,
    book_id: uuid.UUID,
    page_number: int,
    db: DatabaseSession,
    user_context: UserContext
):
    book_file_service = BookFileService(db)
    file_content = await book_file_service.get_book_page(book_id, page_number, user_context)

    return Response(
        content=file_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={book_id}.pdf"}
    )


@book_file_router.get("/{book_id}/file")
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def get_full_book_file(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    book_file_service = BookFileService(db)
    file_content = await book_file_service.get_full_book_file(book_id, user_context)
    
    return Response(
        content=file_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={book_id}.pdf"}
    )


@book_file_router.get("/{book_id}/cover")
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def get_cover(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    book_file_service = BookFileService(db)
    file_content, filename = await book_file_service.get_cover(book_id, user_context)
    
    file_type = None
    if filename[filename.find('.') + 1:] == "png":
        file_type = "image/png"
    elif filename[filename.find('.') + 1:] == "jpg":
        file_type = "image/jpeg"

    return Response(
        content=file_content,
        media_type=file_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

