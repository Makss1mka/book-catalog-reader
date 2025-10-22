from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete
from typing import Optional, List
import uuid
import os
import logging
import PyPDF2
from fastapi import HTTPException

from src.models.entities import Book, AuthorProfile
from src.models.crud_request_dtos import BookCreateDTO, BookUpdateDTO
from src.models.response_dtos import BookResponseDTO
from src.models.enums import BookStatus
from src.exceptions.code_exceptions import NotFoundException, ConflictException, BadRequestException
from src.middlewares.access_control import check_resource_access, get_resource_access_response
from src.middlewares.auth_middleware import UserContext

logger = logging.getLogger(__name__)


class BookService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create_book(
        self, 
        book_data: BookCreateDTO, 
        user_context: UserContext,
        file_content: bytes
    ) -> BookResponseDTO:
        author_query = select(AuthorProfile).where(AuthorProfile.id == uuid.UUID(user_context.user_id))
        author_result = await self.db_session.execute(author_query)
        author = author_result.scalar_one_or_none()
        
        if not author:
            raise NotFoundException("Author not found")
        
        book = Book(
            author_id=uuid.UUID(user_context.user_id),
            title=book_data.title,
            description=book_data.description,
            genres=book_data.genres,
            added_date=datetime.now(),
            status=BookStatus.ON_MODERATE.value,
            file_path=file_path,
        )
        
        file_path = await self._save_book_file(file_content, book.id)
        book.pages_count = await self._count_pdf_pages(file_path)
        
        self.db_session.add(book)
        await self.db_session.commit()
        await self.db_session.refresh(book)
        
        await self._update_author_books_count(user_context.user_id)
        
        return BookResponseDTO.from_entity(book)
    
    async def get_book_by_id(
        self, 
        book_id: str, 
        user_context: UserContext,
        include_author: bool = True
    ) -> BookResponseDTO:
        query = select(Book).where(Book.id == uuid.UUID(book_id))
        
        if include_author:
            query = query.options(selectinload(Book.author))
        
        result = await self.db_session.execute(query)
        book = result.scalar_one_or_none()
        
        if not book:
            raise NotFoundException("Book not found")
        
        if not check_resource_access(
            user_context, 
            book.status, 
            str(book.author_id)
        ):
            raise HTTPException(status_code=403, detail=get_resource_access_response(book.status))
        
        return BookResponseDTO.from_entity(book, include_author)
    
    async def update_book(
        self, 
        book_id: str, 
        book_data: BookUpdateDTO,
        user_context: UserContext
    ) -> BookResponseDTO:
        query = select(Book).where(Book.id == uuid.UUID(book_id))
        result = await self.db_session.execute(query)
        book = result.scalar_one_or_none()
        
        if not book:
            raise NotFoundException("Book not found")
        
        if not self._can_modify_book(user_context, book):
            raise ConflictException("You don't have permission to modify this book")
        
        update_data = {}
        if book_data.title is not None:
            update_data['title'] = book_data.title
        if book_data.description is not None:
            update_data['description'] = book_data.description
        if book_data.genres is not None:
            update_data['genres'] = book_data.genres
        
        if update_data:
            await self.db_session.execute(
                update(Book)
                .where(Book.id == uuid.UUID(book_id))
                .values(**update_data)
            )
            await self.db_session.commit()
            await self.db_session.refresh(book)
        
        return BookResponseDTO.from_entity(book)
    
    async def delete_book(    
        self, 
        book_id: str, 
        user_context: UserContext
    ) -> None:
        query = select(Book).where(Book.id == uuid.UUID(book_id))
        result = await self.db_session.execute(query)
        book = result.scalar_one_or_none()
        
        if not book:
            raise NotFoundException("Book not found")
        
        if not self._can_modify_book(user_context, book):
            raise ConflictException("You don't have permission to delete this book")
        
        if book.file_path and os.path.exists(BOOK_FILES_PATH_DIRECTORY + book.file_path):
            os.remove(BOOK_FILES_PATH_DIRECTORY + book.file_path)
        
        await self.db_session.execute(
            delete(Book).where(Book.id == uuid.UUID(book_id))
        )
        await self.db_session.commit()
        await self._update_author_books_count(str(book.author_id))
    
    async def get_books_by_author(
        self, 
        author_id: str, 
        user_context: UserContext,
        include_author: bool = False
    ) -> List[BookResponseDTO]:
        query = select(Book).where(Book.author_id == uuid.UUID(author_id))
        
        if include_author:
            query = query.options(selectinload(Book.author))
        
        result = await self.db_session.execute(query)
        books = result.scalars().all()
        
        accessible_books = []
        for book in books:
            if check_resource_access(
                user_context, 
                book.status, 
                str(book.author_id)
            ):
                accessible_books.append(BookResponseDTO.from_entity(book, include_author))
        
        return accessible_books
    
    def _can_modify_book(
        self, 
        user_context: UserContext, 
        book: Book
    ) -> bool:
        if user_context.is_admin:
            return True
        
        if user_context.user_id == str(book.author_id):
            return True
        
        return False
    
    async def _save_book_file(
        self, 
        file_content: bytes, 
        book_id: uuid.UUID
    ) -> str:
        os.makedirs(BOOKS_FILES_PATH_DIRECTORY, exist_ok=True)
        
        file_path = BOOKS_FILES_PATH_DIRECTORY + f"{book_id}.pdf"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_path
    
    async def _count_pdf_pages(
        self, 
        file_path: str
    ) -> int:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except ImportError:
            logger.warning("PyPDF2 not installed, cannot count pages")
            return 0
        except Exception as e:
            logger.error(f"Error counting PDF pages: {e}")
            return 0
    
    async def _update_author_books_count(
        self, author_id: str
    ) -> None:
        count_query = select(Book).where(Book.author_id == uuid.UUID(author_id))
        count_result = await self.db_session.execute(count_query)
        books_count = len(count_result.scalars().all())
        
        await self.db_session.execute(
            update(AuthorProfile)
            .where(AuthorProfile.id == uuid.UUID(author_id))
            .values(books_count=books_count)
        )
        await self.db_session.commit()
