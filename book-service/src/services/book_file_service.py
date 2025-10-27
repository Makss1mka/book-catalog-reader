from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import UploadFile
from typing import Optional
import aiofiles
import asyncio
import uuid
import os
import base64
import logging
import PyPDF2
import io

from src.models.entities import Book
from src.models.response_dtos import BookPagesResponseDTO, BookPageResponseDTO, BookResponseDTO
from src.models.enums import BookStatus
from src.exceptions.code_exceptions import ForbiddenException, InternalServerErrorException, NotFoundException, BadRequestException
from src.middlewares.access_control import check_resource_access
from src.middlewares.auth_middleware import UserContext
from src.globals import BOOK_FILES_PATH_DIRECTORY, BOOK_COVERS_PATH_DIRECTORY

logger = logging.getLogger(__name__)


class BookFileService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def set_content_file(
        self,
        book_id: uuid.UUID,
        content_file: UploadFile,
        user_context: UserContext,
    ) -> BookResponseDTO:
        book: Book = await self._get_book(book_id, user_context)
        
        if not self._can_modify_book(user_context, book):
            raise ForbiddenException("You don't have permission to add book file to this entity")

        if content_file.content_type != "application/pdf":
            raise BadRequestException("Content files are only allowed in PDF format")
        
        try:
            book.status = BookStatus.ON_MODERATE
            book.file_path = await self._save_file(content_file, book.id, BOOK_FILES_PATH_DIRECTORY, "pdf")
            book.pages_count = await self._count_pdf_pages(book.file_path)
            
            await self.db_session.commit()
            await self.db_session.refresh(book) 

            return BookResponseDTO.from_entity(book)
        except Exception as e:
            if book.file_path:
                await aiofiles.os.remove(BOOK_FILES_PATH_DIRECTORY + book.file_path)
            logger.exception(e)
            raise InternalServerErrorException("Cannot set book content file cause of some exception")

    async def set_cover_file(
        self,
        book_id: uuid.UUID,
        cover_file: UploadFile,
        user_context: UserContext,
    ) -> BookResponseDTO:
        book: Book = await self._get_book(book_id, user_context)

        if not self._can_modify_book(user_context, book):
            raise ForbiddenException("You don't have permission to set book cover to this entity")

        cover_file_format = None
        if cover_file.content_type == "image/png":
            cover_file_format = "png"
        elif cover_file.content_type == "image/jpeg":
            cover_file_format = "jpg"
        else:
            raise BadRequestException("Cover files are only allowed in PNG or JPG format")
        
        try:
            book.cover_path = await self._save_file(cover_file, book.id, BOOK_COVERS_PATH_DIRECTORY, cover_file_format)

            await self.db_session.commit()
            await self.db_session.refresh(book) 

            return BookResponseDTO.from_entity(book)
        except Exception as e:
            if book.cover_path:
                await aiofiles.os.remove(BOOK_COVERS_PATH_DIRECTORY + book.cover_path)
            logger.exception(e)
            raise InternalServerErrorException("Cannot set book cover file cause of some exception")
    

    async def _save_file(
        self, 
        upload_file: UploadFile, 
        book_id: uuid.UUID,
        save_dir: str,
        file_format: str
    ) -> str:
        await aiofiles.os.makedirs(save_dir, exist_ok=True)
        
        file_path = f"{book_id}.{file_format}"
        full_path = save_dir + "/" + file_path
        
        async with aiofiles.open(full_path, "wb") as f:
            while True:
                chunk = await upload_file.read(4096)
                if not chunk:
                    break
                await f.write(chunk)
        
        await upload_file.seek(0)
        
        return file_path

    async def _count_pdf_pages(
        self, 
        file_path: str
    ) -> int:
        full_path = BOOK_FILES_PATH_DIRECTORY + file_path
        
        def sync_count_pages():
            try: 
                with open(full_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    return len(pdf_reader.pages)
            except ImportError:
                return 0
            except Exception as e:
                raise e

        try:
            logger.debug("HUI 1.3")
            return await asyncio.to_thread(sync_count_pages)
        except Exception as e:
            logger.error(f"Error counting PDF pages: {e}")
            return 0
    
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
    




    async def get_book_pages(
        self,
        book_id: uuid.UUID,
        start_page: int,
        end_page: int,
        user_context: UserContext
    ) -> BookPagesResponseDTO:
        book = await self._get_book(book_id, user_context)
        
        if (
            not book.file_path 
            or not os.path.exists(BOOK_FILES_PATH_DIRECTORY + book.file_path)
        ):
            raise NotFoundException("Cannot find content file of this book")

        if start_page < 1 or end_page < start_page or end_page > book.pages_count:
            raise BadRequestException("Invalid page range")
        
        if not user_context.is_admin and (end_page - start_page + 1) > 10:
            raise BadRequestException("Maximum 10 pages allowed for non-admin users")
        
        return await self._extract_pdf_pages(book.file_path, start_page, end_page)
    
    async def get_book_page(
        self,
        book_id: uuid.UUID,
        page_number: int,
        user_context: UserContext
    ) -> BookPageResponseDTO:
        book = await self._get_book(book_id, user_context)
        
        if (
            not book.file_path 
            or not os.path.exists(BOOK_FILES_PATH_DIRECTORY + book.file_path)
        ):
            raise NotFoundException("Cannot find content file of this book")

        if page_number < 1 or page_number > book.pages_count:
            raise BadRequestException("Invalid page number")
        
        return  await self._extract_pdf_pages(book.file_path, page_number, page_number)
    
    async def get_full_book_file(
        self,
        book_id: uuid.UUID,
        user_context: UserContext
    ) -> bytes:
        book = await self._get_book(book_id, user_context)

        if (
            not book.file_path 
            or not os.path.exists(BOOK_FILES_PATH_DIRECTORY + book.file_path)
        ):
            raise NotFoundException("Cannot find content file of this book")
        
        with open(BOOK_FILES_PATH_DIRECTORY + book.file_path, 'rb') as f:
            return f.read()
    
    async def get_cover(
        self,
        book_id: uuid.UUID,
        user_context: UserContext
    ) -> tuple[bytes, str]:
        book = await self._get_book(book_id, user_context)
        
        if (
            not book.cover_path
            or not os.path.exists(BOOK_COVERS_PATH_DIRECTORY + book.cover_path)
        ):
            raise NotFoundException("Cover file not found")
        
        with open(BOOK_COVERS_PATH_DIRECTORY + book.cover_path, 'rb') as f:
            return f.read(), book.cover_path

    async def _get_book(
        self, 
        book_id: uuid.UUID, 
        user_context:UserContext
    ) -> Book:
        query = select(Book).where(Book.id == book_id)
        result = await self.db_session.execute(query)
        book = result.scalar_one_or_none()
        
        if not book:
            raise NotFoundException("Book not found")

        if not check_resource_access(
            user_context, 
            book.status, 
            book.author_id
        ):
            raise BadRequestException("Access denied to this book")
        
        return book
    
    async def _extract_pdf_pages(
        self, 
        file_path: str, 
        start_page: int, 
        end_page: int
    ) -> bytes:
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
                
                return output_buffer.getvalue()
                
        except ImportError:
            logger.error("PyPDF2 not installed")
            raise BadRequestException("PDF processing not available")
        except Exception as e:
            logger.error(f"Error extracting PDF pages: {e}")
            raise BadRequestException("Error processing PDF file")
