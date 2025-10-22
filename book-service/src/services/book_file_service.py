from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import uuid
import os
import base64
import logging
import PyPDF2
import io

from src.models.entities import Book
from src.models.response_dtos import BookPagesResponseDTO, BookPageResponseDTO
from src.models.enums import BookStatus
from src.exceptions.code_exceptions import NotFoundException, BadRequestException
from src.middlewares.access_control import check_resource_access
from src.middlewares.auth_middleware import UserContext
from src.globals import BOOK_FILES_PATH_DIRECTORY

logger = logging.getLogger(__name__)


class BookFileService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def get_book_pages(
        self,
        book_id: str,
        start_page: int,
        end_page: int,
        user_context: UserContext
    ) -> BookPagesResponseDTO:
        book = await self._get_book(book_id, user_context)
        
        if start_page < 1 or end_page < start_page or end_page > book.pages_count:
            raise BadRequestException("Invalid page range")
        
        if not user_context.is_admin and (end_page - start_page + 1) > 10:
            raise BadRequestException("Maximum 10 pages allowed for non-admin users")
        
        content = await self._extract_pdf_pages(book.file_path, start_page, end_page)
        
        return BookPagesResponseDTO(
            book_id=book_id,
            start_page=start_page,
            end_page=end_page,
            total_pages=book.pages_count,
            content=content
        )
    
    async def get_book_page(
        self,
        book_id: str,
        page_number: int,
        user_context: UserContext
    ) -> BookPageResponseDTO:
        book = await self._get_book(book_id, user_context)
        
        if page_number < 1 or page_number > book.pages_count:
            raise BadRequestException("Invalid page number")
        
        content = await self._extract_pdf_pages(book.file_path, page_number, page_number)
        
        return BookPageResponseDTO(
            book_id=book_id,
            page_number=page_number,
            total_pages=book.pages_count,
            content=content
        )
    
    async def get_full_book_file(
        self,
        book_id: str,
        user_context: UserContext
    ) -> bytes:
        book = await self._get_book(book_id, user_context)
        
        if (
            not book.file_path 
            or not os.path.exists(BOOK_FILES_PATH_DIRECTORY + book.file_path)
        ):
            raise NotFoundException("Book file not found")
        
        with open(BOOK_FILES_PATH_DIRECTORY + book.file_path, 'rb') as f:
            return f.read()
    
    async def _get_book(
        self, 
        book_id: str, 
        user_context:UserContext
    ) -> Book:
        query = select(Book).where(Book.id == uuid.UUID(book_id))
        result = await self.db_session.execute(query)
        book = result.scalar_one_or_none()
        
        if not book:
            raise NotFoundException("Book not found")
        
        if not check_resource_access(
            user_context, 
            book.status, 
            str(book.author_id)
        ):
            raise BadRequestException("Access denied to this book")
        
        return book
    
    async def _extract_pdf_pages(
        self, 
        file_path: str, 
        start_page: int, 
        end_page: int
    ) -> str:
        try:
            with open(BOOK_FILES_PATH_DIRECTORY + file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_writer = PyPDF2.PdfWriter()
                
                for page_num in range(start_page - 1, end_page):
                    if page_num < len(pdf_reader.pages):
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                
                output_buffer = io.BytesIO()
                pdf_writer.write(output_buffer)
                output_buffer.seek(0)
                
                content = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
                
                return content
                
        except ImportError:
            logger.error("PyPDF2 not installed")
            raise BadRequestException("PDF processing not available")
        except Exception as e:
            logger.error(f"Error extracting PDF pages: {e}")
            raise BadRequestException("Error processing PDF file")
