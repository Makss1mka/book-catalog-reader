from src.models.enums import BookStatus, AuthorProfileStatus, ResponseStatus, ResponseDataType
from src.models.entities import Book, AuthorProfile, UserBookStatus
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import date
import logging

logger = logging.getLogger(__name__)


class CommonResponseModel(BaseModel):
    status: ResponseStatus
    data_type: ResponseDataType
    data: Any


class AuthorProfileResponseDTO(BaseModel):
    id: str
    name: str
    rating: float
    common_genres: List[str]
    books_count: int
    reviews_count: int
    likes_count: int
    status: str
    
    @classmethod
    def from_entity(cls, entity: AuthorProfile) -> 'AuthorProfileResponseDTO':
        return cls(
            id=str(entity.id),
            name=entity.name,
            rating=entity.rating,
            common_genres=entity.common_genres or [],
            books_count=entity.books_count,
            reviews_count=entity.reviews_count,
            likes_count=entity.likes_count,
            status=entity.status if hasattr(entity, 'status') else AuthorProfileStatus.ACTIVE.value
        )


class BookResponseDTO(BaseModel):
    id: str
    author_id: str
    title: str
    description: Optional[str]
    file_path: Optional[str]
    cover_path: Optional[str]
    genres: List[str]
    added_date: Optional[date]
    status: str
    total_rating: float
    likes_count: int
    pages_count: int
    reviews_count: int
    is_liked_by_me: Optional[bool]
    author: Optional[AuthorProfileResponseDTO] = None
    
    @classmethod
    def from_entity(cls, entity: Book, include_author: bool = False, count_likes: bool = None, current_user_id: str = None) -> 'BookResponseDTO':
        is_liked_by_me = None
        likes_count = 0

        if count_likes == True and current_user_id != None:
            is_liked_by_me = False

            for like in entity.likers:
                if like.user_id == current_user_id:
                    is_liked_by_me = True
                    break

            likes_count = len(entity.likers)

        return cls(
            id=str(entity.id),
            author_id=str(entity.author_id),
            title=entity.title,
            description=entity.description,
            file_path=entity.file_path,
            cover_path="/api/book-service/books/" + str(entity.id) + "/cover",
            genres=entity.genres or [],
            added_date=entity.added_date,
            status=entity.status,
            total_rating=entity.total_rating,
            likes_count=entity.likes_count,
            pages_count=entity.pages_count,
            reviews_count=entity.reviews_count,
            is_liked_by_me=is_liked_by_me,
            author=AuthorProfileResponseDTO.from_entity(entity.author) if include_author and entity.author else None
        )


class BookSearchResponseDTO(BaseModel):
    books: List[BookResponseDTO]
    total_count: int
    page_number: int
    page_size: int
    total_pages: int


class AuthorProfileSearchResponseDTO(BaseModel):
    authors: List[AuthorProfileResponseDTO]
    total_count: int
    page_number: int
    page_size: int
    total_pages: int


class BookPagesResponseDTO(BaseModel):
    book_id: str
    start_page: int
    end_page: int
    total_pages: int
    content: str  # Base64 encoded content


class BookPageResponseDTO(BaseModel):
    book_id: str
    page_number: int
    total_pages: int
    content: str


class StatusUpdateResponseDTO(BaseModel):
    id: str
    old_status: str
    new_status: str
    message: str




class UserBookStatusResponseDTO(BaseModel):
    book_id: str
    status: str
    author_id: str
    author_name: str
    title: str
    end_page: int
    
    @classmethod
    def from_entity(cls, status: UserBookStatus) -> 'StatusedBookResponseDTO':
        return cls(
            status=status.status,
            book_id=str(status.book_id),
            author_id=str(status.book.author.id),
            author_name=str(status.book.author.name),
            title=status.book.title,
            end_page=status.end_page
        )


class UserBookStatusListResponseDTO(BaseModel):
    books: List[UserBookStatusResponseDTO]
    total_count: int
    page_number: int
    page_size: int
    total_pages: int