from src.exceptions.code_exceptions import ForbiddenException, NotFoundException, ConflictException
from src.middlewares.auth_middleware import UserContext
from src.models.entities import Review, ReviewLike

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class LikeService:
    def __init__(self, db_session: AsyncSession, user_context: UserContext):
        self._db_session = db_session
        self._user_context = user_context
    
    async def add_like(self, review_id: uuid.UUID) -> None:
        review_query = select(Review).where(Review.id == review_id)
        review_result = await self._db_session.execute(review_query)
        review = review_result.scalar_one_or_none()
        
        if not review:
            raise NotFoundException("Review not found")
        
        review_like = ReviewLike(
            review_id=review_id,
            user_id=self._user_context.user_id
        )
        
        try:
            self._db_session.add(review_like)
            await self._db_session.commit()
        except Exception as e:
            logger.exception(e)
            raise ConflictException("Cannot add like cause of some conflicts or ruins of rules")
    
    async def delete_like(self, review_id: uuid.UUID) -> None:
        like_query = select(ReviewLike).where(ReviewLike.review_id == review_id, ReviewLike.user_id == self._user_context.user_id)
        like_result = await self._db_session.execute(like_query)
        like = like_result.scalar_one_or_none()
        
        if not like:
            raise NotFoundException("Like or review not found")
        
        if (
            not self._user_context.is_admin
            and self._user_context.user_id != like.user_id
        ):
            raise ForbiddenException("You don't have permission to delete this like")
        
        await self._db_session.delete(like)
        await self._db_session.commit()
    