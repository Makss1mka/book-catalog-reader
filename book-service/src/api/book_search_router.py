from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime
import logging

from src.annotations import DatabaseSession, UserContext, CommonParams
from src.models.response_dtos import BookSearchResponseDTO
from src.models.enums import UserRole
from src.services.book_search_service import BookSearchService
from src.middlewares.access_control import require_access

logger = logging.getLogger(__name__)

book_search_router = APIRouter(tags=["Book Search"])


@book_search_router.get("/books/search", response_model=BookSearchResponseDTO)
@require_access(
    allowed_roles=[UserRole.GUEST, UserRole.USER, UserRole.ADMIN],
    require_authentication=False
)
async def search_books(
    request: Request,
    db: DatabaseSession,
    user_context: UserContext,
    common_params: CommonParams,
    # Фильтры по книге
    book_rating_min: Optional[float] = Query(None, ge=0, le=5),
    book_rating_max: Optional[float] = Query(None, ge=0, le=5),
    reviews_count_min: Optional[int] = Query(None, ge=0),
    reviews_count_max: Optional[int] = Query(None, ge=0),
    book_likes_min: Optional[int] = Query(None, ge=0),
    book_likes_max: Optional[int] = Query(None, ge=0),
    pages_min: Optional[int] = Query(None, ge=1),
    pages_max: Optional[int] = Query(None, ge=1),
    # Фильтры по автору
    author_rating_min: Optional[float] = Query(None, ge=0, le=5),
    author_rating_max: Optional[float] = Query(None, ge=0, le=5),
    author_likes_min: Optional[int] = Query(None, ge=0),
    author_likes_max: Optional[int] = Query(None, ge=0),
    author_books_min: Optional[int] = Query(None, ge=0),
    author_books_max: Optional[int] = Query(None, ge=0),
    # Фильтры по жанрам
    book_genres: Optional[str] = Query(None),
    author_genres: Optional[str] = Query(None),
    # Фильтры по дате
    added_date_from: Optional[str] = Query(None),
    added_date_to: Optional[str] = Query(None),
    # Поиск по ключевой строке
    key: Optional[str] = Query(None)
):
    search_params = {}

    if book_rating_min is not None:
        search_params['book_rating_min'] = book_rating_min
    if book_rating_max is not None:
        search_params['book_rating_max'] = book_rating_max
    if reviews_count_min is not None:
        search_params['reviews_count_min'] = reviews_count_min
    if reviews_count_max is not None:
        search_params['reviews_count_max'] = reviews_count_max
    if book_likes_min is not None:
        search_params['book_likes_min'] = book_likes_min
    if book_likes_max is not None:
        search_params['book_likes_max'] = book_likes_max
    if pages_min is not None:
        search_params['pages_min'] = pages_min
    if pages_max is not None:
        search_params['pages_max'] = pages_max
    
    if author_rating_min is not None:
        search_params['author_rating_min'] = author_rating_min
    if author_rating_max is not None:
        search_params['author_rating_max'] = author_rating_max
    if author_likes_min is not None:
        search_params['author_likes_min'] = author_likes_min
    if author_likes_max is not None:
        search_params['author_likes_max'] = author_likes_max
    if author_books_min is not None:
        search_params['author_books_min'] = author_books_min
    if author_books_max is not None:
        search_params['author_books_max'] = author_books_max
    
    if book_genres:
        search_params['book_genres'] = book_genres.split(',')
    if author_genres:
        search_params['author_genres'] = author_genres.split(',')
    
    if added_date_from:
        try:
            search_params['added_date_from'] = datetime.strptime(added_date_from, "%Y-%m-%d").date()
        except ValueError:
            pass
    if added_date_to:
        try:
            search_params['added_date_to'] = datetime.strptime(added_date_to, "%Y-%m-%d").date()
        except ValueError:
            pass
    
    if key:
        search_params['key'] = key
    
    search_service = BookSearchService(db)
    return await search_service.search_books(
        user_context=user_context,
        search_params=search_params,
        page_number=common_params['page_number'],
        page_size=common_params['page_size'],
        sort_by=common_params['sort_by'],
        sort_order=common_params['sort_order']
    )
