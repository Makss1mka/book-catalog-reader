from src.models.entities import Review
from pydantic import BaseModel
from datetime import datetime
from typing import List

class ReviewResponseDTO(BaseModel):
    id: str
    book_id: str
    user_id: str
    user_name: str
    text: str
    rating: int
    added_date: datetime
    
    @classmethod
    def from_entity(cls, entity: Review) -> 'ReviewResponseDTO':
        return cls(
            id=str(entity.id),
            book_id=str(entity.book_id),
            user_id=str(entity.user_id),
            user_name=entity.user_name,
            text=entity.text,
            rating=entity.rating,
            added_date=entity.added_date,
        )

class ReviewsListResponseDTO(BaseModel):
    reviews: List[ReviewResponseDTO]
    total_count: int
    page_number: int
    page_size: int
    total_pages: int
