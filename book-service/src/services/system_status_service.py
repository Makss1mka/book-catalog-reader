from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
import uuid
import logging

from src.models.entities import Book, AuthorProfile
from src.models.crud_request_dtos import BookStatusUpdateDTO, AuthorProfileStatusUpdateDTO
from src.models.response_dtos import StatusUpdateResponseDTO
from src.models.enums import BookStatus, AuthorProfileStatus
from src.exceptions.code_exceptions import NotFoundException, ConflictException, BadRequestException
from src.middlewares.access_control import check_resource_access
from src.middlewares.auth_middleware import UserContext

logger = logging.getLogger(__name__)


class StatusService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def update_book_status(
        self,
        book_id: uuid.UUID,
        status_data: BookStatusUpdateDTO,
        user_context: UserContext
    ) -> StatusUpdateResponseDTO:
        query = select(Book).where(Book.id == book_id)
        result = await self.db_session.execute(query)
        book = result.scalar_one_or_none()
        
        if not book:
            raise NotFoundException("Book not found")
        
        old_status = book.status
        new_status = status_data.status.value
        
        if not self._can_change_book_status(user_context, book, new_status):
            raise ConflictException("You don't have permission to change book status")
        
        if not self._is_valid_book_status_transition(old_status, new_status, user_context):
            raise BadRequestException(f"Invalid status transition from {old_status} to {new_status}")
        
        await self.db_session.execute(
            update(Book)
            .where(Book.id == book_id)
            .values(status=new_status)
        )
        await self.db_session.commit()
        
        return StatusUpdateResponseDTO(
            id=str(book_id),
            old_status=old_status,
            new_status=new_status,
            message=f"Book status changed from {old_status} to {new_status}"
        )
    
    async def update_author_profile_status(
        self,
        author_id: uuid.UUID,
        status_data: AuthorProfileStatusUpdateDTO,
        user_context: UserContext
    ) -> StatusUpdateResponseDTO:
        query = select(AuthorProfile).where(AuthorProfile.id == author_id)
        result = await self.db_session.execute(query)
        author_profile = result.scalar_one_or_none()
        
        if not author_profile:
            raise NotFoundException("Author profile not found")
        
        old_status = author_profile.status
        new_status = status_data.status.value
        
        if not self._can_change_author_status(user_context, author_profile, new_status):
            raise ConflictException("You don't have permission to change author profile status")
        
        if not self._is_valid_author_status_transition(old_status, new_status, user_context):
            raise BadRequestException(f"Invalid status transition from {old_status} to {new_status}")
        
        await self.db_session.execute(
            update(AuthorProfile)
            .where(AuthorProfile.id == author_id)
            .values(status=new_status)
        )
        await self.db_session.commit()
        
        return StatusUpdateResponseDTO(
            id=str(author_id),
            old_status=old_status,
            new_status=new_status,
            message=f"Author profile status changed from {old_status} to {new_status}"
        )
    
    def _can_change_book_status(
        self, 
        user_context: UserContext, 
        book: Book, 
        new_status: str
    ) -> bool:
        if user_context.is_admin:
            return True
        
        if user_context.user_id == str(book.author_id):
            allowed_author_statuses = [BookStatus.PRIVATE.value, BookStatus.ACTIVE.value]
            return new_status in allowed_author_statuses
        
        return False
    
    def _can_change_author_status(
        self, 
        user_context: UserContext, 
        author_profile: AuthorProfile, 
        new_status: str
    ) -> bool:
        if user_context.is_admin:
            return True
        
        if user_context.user_id == str(author_profile.user_id):
            allowed_owner_statuses = [AuthorProfileStatus.PRIVATE.value, AuthorProfileStatus.ACTIVE.value]
            return new_status in allowed_owner_statuses
        
        return False
    
    def _is_valid_book_status_transition(
        self, 
        old_status: str, 
        new_status: str, 
        user_context: UserContext
    ) -> bool:
        if user_context.is_admin:
            return True
        
        valid_transitions = {
            BookStatus.ACTIVE.value: [BookStatus.PRIVATE.value],
            BookStatus.PRIVATE.value: [BookStatus.ACTIVE.value]
        }
        
        return new_status in valid_transitions.get(old_status, [])
    
    def _is_valid_author_status_transition(
        self, 
        old_status: str, 
        new_status: str, 
        user_context: UserContext
    ) -> bool:
        if user_context.is_admin:
            return True
        
        valid_transitions = {
            AuthorProfileStatus.ACTIVE.value: [AuthorProfileStatus.PRIVATE.value],
            AuthorProfileStatus.PRIVATE.value: [AuthorProfileStatus.ACTIVE.value]
        }
        
        return new_status in valid_transitions.get(old_status, [])
