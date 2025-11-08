from src.models.entities import Review
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ReviewResponseDTO(BaseModel):
    id: str
    book_id: str
    user_id: str
    user_name: str
    text: str
    rating: int
    added_date: datetime
    is_liked_by_me: Optional[bool]
    likes_count: Optional[int]
    
    @classmethod
    def from_entity(cls, entity: Review, count_likes: bool = None, current_user_id: str = None) -> 'ReviewResponseDTO':
        is_liked_by_me = None
        likes_count = None

        if count_likes == True and current_user_id != None:
            is_liked_by_me = False

            for like in entity.likers:
                if like.user_id == current_user_id:
                    is_liked_by_me = True
                    break

            likes_count = len(entity.likers)

        return cls(
            id=str(entity.id),
            book_id=str(entity.book_id),
            user_id=str(entity.user_id),
            user_name=entity.user_name,
            text=entity.text,
            rating=entity.rating,
            added_date=entity.added_date,
            is_liked_by_me=is_liked_by_me,
            likes_count=likes_count,
        )

class ReviewsListResponseDTO(BaseModel):
    reviews: List[ReviewResponseDTO]
    total_count: int
    page_number: int
    page_size: int
    total_pages: int
