import email
from src.models.enums import UserStatus
from src.models.response_dtos import UserProfileResponseDTO, UserResponseDTO
from src.models.request_dtos import UserUpdateDTO
from src.middlewares.access_control import check_resource_access
from src.middlewares.auth_middleware import UserContext
from src.models.entities import User, UserProfile
from src.exceptions.code_exceptions import (
    ForbiddenException, NoContentException, NotFoundException, BadRequestException, ConflictException,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.orm import joinedload
from sqlalchemy import select, or_
from passlib.hash import bcrypt
from uuid import UUID

import datetime
import logging

logger: logging.Logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db_session: AsyncSession, user_context: UserContext):
        self.db_session = db_session
        self.user_context = user_context

    async def _get_user_entity_by_id(self, user_id: UUID) -> User:
        user_query = select(User).where(User.id == user_id).options(joinedload(User.profile))
        user_result = await self.db_session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User not found")

        if not check_resource_access(
            user_context=self.user_context,
            resource_status=user.status,
            resource_owner_id=user.id
        ): 
            raise ForbiddenException("Access denied")

        return user


    async def get_user_by_id(self, user_id: UUID) -> UserResponseDTO:
        user = await self._get_user_entity_by_id(user_id)

        return UserResponseDTO.from_entity(user)

    async def get_user_profile_by_id(self, user_id: UUID) -> UserProfileResponseDTO:
        user = await self._get_user_entity_by_id(user_id)

        return UserProfileResponseDTO.from_entity(user.profile)


    async def update_user(self, user_id: UUID, update_user_dto: UserUpdateDTO) -> UserResponseDTO:
        user = await self._get_user_entity_by_id(user_id)

        try:
            is_smth_updated = False

            if update_user_dto.username:
                is_smth_updated = True
                user.profile.username = update_user_dto.username

            if is_smth_updated:
                await self.db_session.commit()
                await self.db_session.refresh(user)
                
                return UserResponseDTO.from_entity(user)
            else:
                raise NoContentException("Nothing changed cause of empty body")
        except IntegrityError as e:
            raise ConflictException("This user data ruins some constrains") from e


    async def delete_user(self, user_id: UUID) -> str:
        await self.db_session.delete(
            await self._get_user_entity_by_id(user_id)
        )

        return "User was deleted"
