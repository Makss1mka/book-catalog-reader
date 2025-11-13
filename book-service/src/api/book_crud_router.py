from src.models.crud_request_dtos import BookCreateDTO, BookUpdateDTO
from src.models.enums import ResponseDataType, ResponseStatus
from src.middlewares.access_control import require_access
from src.models.response_dtos import CommonResponseModel
from src.annotations import DatabaseSession, UserContext
from src.services.book_service import BookService
from src.models.enums import UserRole

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
import logging
import uuid



logger = logging.getLogger(__name__)

book_crud_router = APIRouter(prefix="/books", tags=["Books CRUD"])


@book_crud_router.post("/", response_class=JSONResponse, status_code=201)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def create_book(
    request: Request,
    db: DatabaseSession,
    user_context: UserContext,
    book_data: BookCreateDTO
):
    book_service = BookService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await book_service.create_book(book_data, user_context)
    )


@book_crud_router.get("/{book_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.GUEST, UserRole.USER, UserRole.ADMIN],
    require_authentication=False
)
async def get_book(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):  
    book_service = BookService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await book_service.get_book_by_id(book_id, user_context, include_author=True)
    )


@book_crud_router.put("/{book_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def update_book(
    request: Request,
    book_id: uuid.UUID,
    book_data: BookUpdateDTO,
    db: DatabaseSession,
    user_context: UserContext
):
    book_service = BookService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await book_service.update_book(book_id, book_data, user_context)
    )


@book_crud_router.delete("/{book_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def delete_book(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    book_service = BookService(db)
    await book_service.delete_book(book_id, user_context)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.STRING,
        data="Book deleted successfully"
    )


@book_crud_router.get("/author/{author_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.GUEST, UserRole.USER, UserRole.ADMIN],
    require_authentication=False
)
async def get_books_by_author(
    request: Request,
    author_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    book_service = BookService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await book_service.get_books_by_author(author_id, user_context, include_author=True)
    )