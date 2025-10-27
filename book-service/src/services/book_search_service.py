from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, and_, or_, desc, asc, literal
from typing import Optional, List, Dict, Any
import logging
from datetime import date
from fastapi import HTTPException

from src.models.entities import Book, AuthorProfile
from src.models.response_dtos import BookSearchResponseDTO, BookResponseDTO
from src.models.enums import BookStatus
from src.exceptions.code_exceptions import BadRequestException
from src.middlewares.access_control import check_resource_access, get_resource_access_response
from src.middlewares.auth_middleware import UserContext

logger = logging.getLogger(__name__)


class BookSearchService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def search_books(
        self,
        user_context: UserContext,
        search_params: Dict[str, Any],
        page_number: int = 1,
        page_size: int = 10,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None
    ) -> BookSearchResponseDTO:
        if not user_context.is_admin and page_size > 20:
            raise BadRequestException("Maximum 20 pages allowed for non-admin users")
        
        query = select(Book).options(selectinload(Book.author))
        query = query.join(AuthorProfile, Book.author_id == AuthorProfile.id)

        conditions = []

        if not user_context.is_admin:
            conditions.append(Book.status == BookStatus.ACTIVE.value)
        
        if 'book_rating_min' in search_params:
            conditions.append(Book.total_rating >= search_params['book_rating_min'])
        if 'book_rating_max' in search_params:
            conditions.append(Book.total_rating <= search_params['book_rating_max'])

        if 'author_rating_min' in search_params:
            conditions.append(AuthorProfile.rating >= search_params['author_rating_min'])
        if 'author_rating_max' in search_params:
            conditions.append(AuthorProfile.rating <= search_params['author_rating_max'])
        
        if 'reviews_count_min' in search_params:
            conditions.append(Book.reviews_count >= search_params['reviews_count_min'])
        if 'reviews_count_max' in search_params:
            conditions.append(Book.reviews_count <= search_params['reviews_count_max'])
        
        if 'book_likes_min' in search_params:
            conditions.append(Book.likes_count >= search_params['book_likes_min'])
        if 'book_likes_max' in search_params:
            conditions.append(Book.likes_count <= search_params['book_likes_max'])
        
        if 'author_likes_min' in search_params:
            conditions.append(AuthorProfile.likes_count >= search_params['author_likes_min'])
        if 'author_likes_max' in search_params:
            conditions.append(AuthorProfile.likes_count <= search_params['author_likes_max'])
 
        if 'author_books_min' in search_params:
            conditions.append(AuthorProfile.books_count >= search_params['author_books_min'])
        if 'author_books_max' in search_params:
            conditions.append(AuthorProfile.books_count <= search_params['author_books_max'])
        
        if 'book_genres' in search_params and search_params['book_genres']:
            genres = [genre.strip() for genre in search_params['book_genres']]
            for genre in genres:
                conditions.append(Book.genres.contains(genre))
        
        if 'author_genres' in search_params and search_params['author_genres']:
            author_genres = [genre.strip() for genre in search_params['author_genres']]
            for genre in author_genres:
                conditions.append(AuthorProfile.common_genres.contains(genre))
        
        if 'added_date_from' in search_params:
            conditions.append(Book.added_date >= search_params['added_date_from'])
        if 'added_date_to' in search_params:
            conditions.append(Book.added_date <= search_params['added_date_to'])
        
        if 'pages_min' in search_params:
            conditions.append(Book.pages_count >= search_params['pages_min'])
        if 'pages_max' in search_params:
            conditions.append(Book.pages_count <= search_params['pages_max'])
        
        if 'key' in search_params and search_params['key']:
            key = search_params['key'].strip()
            if key:
                conditions.append(or_(
                    literal(f" {Book.title.lower()} ").like(f"% {key.lower()}%"),
                    literal(f" {AuthorProfile.name.lower()} ").like(f"% {key.lower()}%")
                ))
        
        if conditions:
            query = query.where(and_(*conditions))
        
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db_session.execute(count_query)
        total_count = count_result.scalar()
        
        if sort_by:
            sort_column = self._get_sort_column(sort_by)
            if sort_column:
                if sort_order == 'desc':
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(asc(sort_column))
        
        offset = (page_number - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db_session.execute(query)
        books = result.scalars().all()
        
        accessible_books = []
        for book in books:
            if check_resource_access(
                user_context, 
                book.status, 
                book.author_id
            ):
                accessible_books.append(BookResponseDTO.from_entity(book, include_author=True))
    
        total_pages = (total_count + page_size - 1) // page_size
        
        return BookSearchResponseDTO(
            books=accessible_books,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
            total_pages=total_pages
        )
    
    def _get_sort_column(self, sort_by: str):
        sort_columns = {
            'title': Book.title,
            'rating': Book.total_rating,
            'likes': Book.likes_count,
            'reviews': Book.reviews_count,
            'pages': Book.pages_count,
            'issued_date': Book.issued_date,
            'author_rating': AuthorProfile.rating,
            'author_likes': AuthorProfile.likes_count,
            'author_books': AuthorProfile.books_count
        }
        return sort_columns.get(sort_by)
