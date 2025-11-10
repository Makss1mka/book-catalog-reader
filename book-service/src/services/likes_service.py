from src.exceptions.code_exceptions import ForbiddenException, NotFoundException, ConflictException
from src.middlewares.auth_middleware import UserContext
from src.models.entities import Book, BookLike

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
import uuid

logger = logging.getLogger(__name__)


class LikesService:
    def __init__(self, db_session: AsyncSession, user_context: UserContext):
        self._db_session = db_session
        self._user_context = user_context
    
    async def add_like(self, book_id: uuid.UUID) -> None:
        book_query = select(Book).where(Book.id == book_id)
        book_result = await self._db_session.execute(book_query)
        book = book_result.scalar_one_or_none()
        
        if not book:
            raise NotFoundException("Book not found")
        
        book_like = BookLike(
            book_id=book_id,
            user_id=self._user_context.user_id
        )
        
        try:
            self._db_session.add(book_like)
            await self._db_session.commit()
        except Exception as e:
            logger.exception(e)
            raise ConflictException("Cannot add like cause of some conflicts or ruins of rules")
    
    async def delete_like(self, book_id: uuid.UUID) -> None:
        like_query = select(BookLike).where(BookLike.book_id == book_id, BookLike.user_id == self._user_context.user_id)
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
    