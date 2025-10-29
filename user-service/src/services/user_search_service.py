from src.models.response_dtos import UserProfileResponseDTO, UserResponseDTO
from src.models.crud_request_dtos import CreateUserRequest, UpdateUserRequest
from src.middlewares.access_control import check_resource_access
from src.middlewares.auth_middleware import UserContext
from src.models.entities import User, UserProfile
from src.exceptions.code_exceptions import (
    ForbiddenException, NotFoundException, BadRequestException, ConflictException,
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


class UserSearchService:
    def __init__(self, db_session: AsyncSession, user_context: UserContext):
        self.db_session = db_session
        self.user_context = user_context

    async def get_user_entity_by_login_or_email(self, login: str = "", email: str = "") -> User:
        user_query = select(User).where(or_(User.login == login, User.email == email)).options(joinedload(User.profile))
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
