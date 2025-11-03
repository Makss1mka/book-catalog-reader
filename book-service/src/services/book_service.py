from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete
from typing import Optional, List
from datetime import datetime
import uuid
import os
import logging
import PyPDF2
from fastapi import HTTPException, UploadFile
import aiofiles
import aiofiles.os
import asyncio

from src.models.entities import Book, AuthorProfile
from src.models.crud_request_dtos import BookCreateDTO, BookUpdateDTO
from src.models.response_dtos import BookResponseDTO
from src.models.enums import BookStatus
from src.exceptions.code_exceptions import ForbiddenException, InternalServerErrorException, NotFoundException, ConflictException, BadRequestException
from src.middlewares.access_control import check_resource_access, get_resource_access_response
from src.middlewares.auth_middleware import UserContext
from src.globals import BOOK_FILES_PATH_DIRECTORY, BOOK_COVERS_PATH_DIRECTORY

logger = logging.getLogger(__name__)


class BookService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create_book(
        self, 
        book_data: BookCreateDTO, 
        user_context: UserContext
    ) -> BookResponseDTO:
        author_query = select(AuthorProfile).where(AuthorProfile.user_id == user_context.user_id)
        author_result = await self.db_session.execute(author_query)
        author = author_result.scalar_one_or_none()
        
        if not author:
            raise NotFoundException("Author not found")
        
        book = Book(
            id=uuid.uuid4(),
            author_id=user_context.user_id,
            title=book_data.title,
            description=book_data.description,
            genres=book_data.genres,
            added_date=datetime.now(),
            status=BookStatus.WAIT_FILE.value
        )
        
        try:
            self.db_session.add(book)
            await self._update_author_books_count(user_context.user_id)
            await self.db_session.commit()
            await self.db_session.refresh(book) 
        except Exception as e:
            if book.file_path:
                await aiofiles.os.remove(BOOK_FILES_PATH_DIRECTORY + book.file_path)
            if book.cover_path:
                await aiofiles.os.remove(BOOK_COVERS_PATH_DIRECTORY + book.cover_path)
            logger.exception(e)
            raise ConflictException("Cannot create book cause of some conflicts or ruins of rules")
        
        return BookResponseDTO.from_entity(book, False)
    
    async def get_book_by_id(
        self, 
        book_id: uuid.UUID, 
        user_context: UserContext,
        include_author: bool = True
    ) -> BookResponseDTO:
        query = select(Book).where(Book.id == book_id)
        
        if include_author:
            query = query.options(selectinload(Book.author))
        
        result = await self.db_session.execute(query)
        book = result.scalar_one_or_none()
        
        if not book:
            raise NotFoundException("Book not found")
        
        if not check_resource_access(
            user_context, 
            book.status, 
            book.author_id
        ):
            raise HTTPException(status_code=403, detail=get_resource_access_response(book.status))
        
        return BookResponseDTO.from_entity(book, include_author)
    
    async def update_book(
        self, 
        book_id: uuid.UUID, 
        book_data: BookUpdateDTO,
        user_context: UserContext
    ) -> BookResponseDTO:
        query = select(Book).where(Book.id == book_id)
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
                .where(Book.id == book_id)
                .values(**update_data)
            )
            await self.db_session.commit()
            await self.db_session.refresh(book)
        
        return BookResponseDTO.from_entity(book)
    
    async def delete_book(
        self, 
        book_id: uuid.UUID, 
        user_context: UserContext
    ) -> None:
        query = select(Book).where(Book.id == book_id)
        result = await self.db_session.execute(query)
        book = result.scalar_one_or_none()
        
        if not book:
            raise NotFoundException("Book not found")
        
        if not self._can_modify_book(user_context, book):
            raise ForbiddenException("You don't have permission to delete this book")
        
        full_file_path = (BOOK_FILES_PATH_DIRECTORY + book.file_path) if book.file_path else None
        
        if full_file_path and await aiofiles.os.path.exists(full_file_path):
            await aiofiles.os.remove(full_file_path)
        
        await self.db_session.execute(
            delete(Book).where(Book.id == book_id)
        )
        await self.db_session.commit()
        await self._update_author_books_count(book.author_id)
    
    async def get_books_by_author(
        self, 
        author_id: uuid.UUID, 
        user_context: UserContext,
        include_author: bool = False
    ) -> List[BookResponseDTO]:
        query = select(Book).where(Book.author_id == author_id)
        
        if include_author:
            query = query.options(selectinload(Book.author))
        
        result = await self.db_session.execute(query)
        books = result.scalars().all()
        
        accessible_books = []
        for book in books:
            if check_resource_access(
                user_context, 
                book.status, 
                book.author_id
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
        
        if user_context.user_id == book.author_id:
            return True
        
        return False
    
    async def _update_author_books_count(
        self, author_id: uuid.UUID
    ) -> None:
        count_query = select(Book).where(Book.author_id == author_id)
        count_result = await self.db_session.execute(count_query)
        books_count = len(count_result.scalars().all())
        
        await self.db_session.execute(
            update(AuthorProfile)
            .where(AuthorProfile.id == author_id)
            .values(books_count=books_count)
        )
