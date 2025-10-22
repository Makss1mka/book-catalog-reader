from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging

from src.annotations import DatabaseSession, UserContext
from src.models.crud_request_dtos import BookCreateDTO, BookUpdateDTO
from src.models.response_dtos import BookResponseDTO
from src.models.enums import UserRole
from src.services.book_service import BookService
from src.middlewares.access_control import require_access
from src.exceptions.code_exceptions import BadRequestException

logger = logging.getLogger(__name__)

book_crud_router = APIRouter(prefix="/books", tags=["Books CRUD"])


@book_crud_router.post("/", response_model=BookResponseDTO)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def create_book(
    request: Request,
    db: DatabaseSession,
    user_context: UserContext,
    title: str = Form(...),
    description: Optional[str] = Form("No description"),
    genres: Optional[list[str]] = Form(list()),
    file: UploadFile = File(...)
):
    if file.content_type != "application/pdf":
        raise BadRequestException("Only PDF files are allowed")
    
    file_content = await file.read()

    book_data = BookCreateDTO(
        title=title,
        description=description,
        genres=genres
    )

    book_service = BookService(db)
    return await book_service.create_book(book_data, user_context, file_content)


@book_crud_router.get("/{book_id}", response_model=BookResponseDTO)
@require_access(
    allowed_roles=[UserRole.GUEST, UserRole.USER, UserRole.ADMIN],
    require_authentication=False
)
async def get_book(
    request: Request,
    book_id: str,
    db: DatabaseSession,
    user_context: UserContext
):  
    book_service = BookService(db)
    return await book_service.get_book_by_id(book_id, user_context, include_author=True)


@book_crud_router.put("/{book_id}", response_model=BookResponseDTO)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def update_book(
    request: Request,
    book_id: str,
    book_data: BookUpdateDTO,
    db: DatabaseSession,
    user_context: UserContext
):
    book_service = BookService(db)
    return await book_service.update_book(book_id, book_data, user_context)


@book_crud_router.delete("/{book_id}")
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def delete_book(
    request: Request,
    book_id: str,
    db: DatabaseSession,
    user_context: UserContext
):
    book_service = BookService(db)
    await book_service.delete_book(book_id, user_context)
    return {"message": "Book deleted successfully"}


@book_crud_router.get("/author/{author_id}", response_model=list[BookResponseDTO])
@require_access(
    allowed_roles=[UserRole.GUEST, UserRole.USER, UserRole.ADMIN],
    require_authentication=False
)
async def get_books_by_author(
    request: Request,
    author_id: str,
    db: DatabaseSession,
    user_context: UserContext
):
    book_service = BookService(db)
    return await book_service.get_books_by_author(author_id, user_context, include_author=True)

