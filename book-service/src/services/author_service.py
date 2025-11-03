from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete
from typing import Optional, List
import uuid
import logging
from fastapi import HTTPException

from src.models.entities import AuthorProfile, Book
from src.models.crud_request_dtos import AuthorProfileCreateDTO, AuthorProfileUpdateDTO
from src.models.response_dtos import AuthorProfileResponseDTO
from src.models.enums import AuthorProfileStatus
from src.exceptions.code_exceptions import ForbiddenException, NotFoundException, ConflictException, BadRequestException
from src.middlewares.access_control import check_resource_access, get_resource_access_response
from src.middlewares.auth_middleware import UserContext

logger = logging.getLogger(__name__)


class AuthorProfileService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create_author_profile(
        self, 
        author_data: AuthorProfileCreateDTO, 
        user_id: uuid.UUID
    ) -> AuthorProfileResponseDTO:
        existing_query = select(AuthorProfile).where(
            AuthorProfile.user_id == user_id
        )
        existing_result = await self.db_session.execute(existing_query)
        existing_profile = existing_result.scalar_one_or_none()
        
        if existing_profile:
            raise ConflictException("Author profile already exists for this user")
        
        author_profile = AuthorProfile(
            id=user_id,
            user_id=user_id,
            name=author_data.name,
            common_genres=author_data.common_genres,
            status=AuthorProfileStatus.ACTIVE.value
        )
        
        try:
            self.db_session.add(author_profile)
            await self.db_session.commit()
            await self.db_session.refresh(author_profile)
        except Exception as e:
            logger.exception(e)
            raise ConflictException("Occures some conflicts while creating new author profile")

        return AuthorProfileResponseDTO.from_entity(author_profile)
    
    async def get_author_profile_by_id(
        self, 
        author_id: uuid.UUID, 
        user_context: UserContext,
        include_books: bool = True
    ) -> AuthorProfileResponseDTO:
        query = select(AuthorProfile).where(AuthorProfile.id == author_id)
        
        if include_books:
            query = query.options(selectinload(AuthorProfile.books))
        
        result = await self.db_session.execute(query)
        author_profile = result.scalar_one_or_none()
        
        if not author_profile:
            raise NotFoundException("Author profile not found")
        
        if not check_resource_access(
            user_context, 
            author_profile.status, 
            author_profile.user_id
        ):
            raise HTTPException(status_code=403, detail=get_resource_access_response(author_profile.status))
        
        return AuthorProfileResponseDTO.from_entity(author_profile)
    
    async def update_author_profile(
        self, 
        author_id: uuid.UUID, 
        author_data: AuthorProfileUpdateDTO,
        user_context: UserContext
    ) -> AuthorProfileResponseDTO:
        query = select(AuthorProfile).where(AuthorProfile.id == author_id)
        result = await self.db_session.execute(query)
        author_profile = result.scalar_one_or_none()
        
        if not author_profile:
            raise NotFoundException("Author profile not found")
        
        if not self._can_modify_author_profile(user_context, author_profile):
            raise ForbiddenException("You don't have permission to modify this author profile")
        
        update_data = {}
        if author_data.name is not None:
            update_data['name'] = author_data.name
        if author_data.common_genres is not None:
            update_data['common_genres'] = author_data.common_genres
        
        if update_data:
            await self.db_session.execute(
                update(AuthorProfile)
                .where(AuthorProfile.id == author_id)
                .values(**update_data)
            )
            await self.db_session.commit()
            await self.db_session.refresh(author_profile)
        
        return AuthorProfileResponseDTO.from_entity(author_profile)
    
    async def delete_author_profile(
        self, 
        author_id: uuid.UUID, 
        user_context: UserContext
    ) -> None:
        query = select(AuthorProfile).where(AuthorProfile.id == author_id)
        result = await self.db_session.execute(query)
        author_profile = result.scalar_one_or_none()
        
        if not author_profile:
            raise NotFoundException("Author profile not found")
        
        if not self._can_modify_author_profile(user_context, author_profile):
            raise ConflictException("You don't have permission to delete this author profile")
        
        books_query = select(Book).where(Book.author_id == author_id)
        books_result = await self.db_session.execute(books_query)
        books = books_result.scalars().all()
        
        if books:
            raise ConflictException("Cannot delete author profile with existing books")
        
        await self.db_session.execute(
            delete(AuthorProfile).where(AuthorProfile.id == author_id)
        )
        await self.db_session.commit()
    
    async def get_all_author_profiles(
        self, 
        user_context: UserContext,
        include_books: bool = False
    ) -> List[AuthorProfileResponseDTO]:
        query = select(AuthorProfile)
        
        if include_books:
            query = query.options(selectinload(AuthorProfile.books))
        
        result = await self.db_session.execute(query)
        author_profiles = result.scalars().all()
        
        accessible_profiles = []
        for profile in author_profiles:
            if check_resource_access(
                user_context, 
                profile.status, 
                profile.user_id
            ):
                accessible_profiles.append(AuthorProfileResponseDTO.from_entity(profile))
        
        return accessible_profiles
    
    async def _get_author_profile_by_user_id_internal(
        self, 
        user_id: uuid.UUID, 
        include_books: bool = True
    ) -> AuthorProfileResponseDTO:
        query = select(AuthorProfile).where(
            AuthorProfile.user_id == user_id
        )
        
        if include_books:
            query = query.options(selectinload(AuthorProfile.books))
        
        result = await self.db_session.execute(query)
        author_profile = result.scalar_one_or_none()
        
        if not author_profile:
            raise NotFoundException("Author profile not found")
        
        return AuthorProfileResponseDTO.from_entity(author_profile)
    
    async def update_author_statistics(self, author_id: uuid.UUID) -> None:
        books_query = select(Book).where(Book.author_id == author_id)
        books_result = await self.db_session.execute(books_query)
        books = books_result.scalars().all()
        
        if not books:
            return
        
        total_rating = sum(book.total_rating for book in books)
        books_count = len(books)
        reviews_count = sum(book.reviews_count for book in books)
        likes_count = sum(book.likes_count for book in books)
        
        average_rating = total_rating / books_count if books_count > 0 else 0.0
        
        await self.db_session.execute(
            update(AuthorProfile)
            .where(AuthorProfile.id == author_id)
            .values(
                rating=average_rating,
                books_count=books_count,
                reviews_count=reviews_count,
                likes_count=likes_count
            )
        )
        await self.db_session.commit()
    
    def _can_modify_author_profile(
        self, 
        user_context: UserContext, 
        author_profile: AuthorProfile
    ) -> bool:
        if user_context.is_admin:
            return True
        
        if user_context.user_id == author_profile.user_id:
            return True
        
        return False
