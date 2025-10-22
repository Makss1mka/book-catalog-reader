from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from src.models.enums import BookStatus, AuthorProfileStatus
from src.models.entities import Book, AuthorProfile


class AuthorProfileResponseDTO(BaseModel):
    id: str
    user_profile_id: str
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
            user_profile_id=str(entity.user_profile_id),
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
    genres: List[str]
    issued_date: Optional[date]
    status: str
    total_rating: float
    likes_count: int
    pages_count: int
    reviews_count: int
    author: Optional[AuthorProfileResponseDTO] = None
    
    @classmethod
    def from_entity(cls, entity: Book, include_author: bool = False) -> 'BookResponseDTO':
        return cls(
            id=str(entity.id),
            author_id=str(entity.author_id),
            title=entity.title,
            description=entity.description,
            file_path=entity.file_path,
            genres=entity.genres or [],
            issued_date=entity.issued_date,
            status=entity.status,
            total_rating=entity.total_rating,
            likes_count=entity.likes_count,
            pages_count=entity.pages_count,
            reviews_count=entity.reviews_count,
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
    content: str  # Base64 encoded content


class StatusUpdateResponseDTO(BaseModel):
    id: str
    old_status: str
    new_status: str
    message: str

