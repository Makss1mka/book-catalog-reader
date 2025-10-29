import email
from src.models.enums import UserStatus
from src.models.response_dtos import UserResponseDTO
from src.models.request_dtos import UserRegistrationDTO, UserAuthDTO
from src.middlewares.access_control import check_resource_access
from src.middlewares.auth_middleware import UserContext
from src.models.entities import User, UserProfile
from src.globals import TOKEN_SECRET, TOKEN_TTL
from src.exceptions.code_exceptions import (
    ForbiddenException, NoContentException, NotFoundException, BadRequestException, ConflictException, UnauthorizedException,
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, DBAPIError
from sqlalchemy.orm import joinedload
from sqlalchemy import select, or_
from passlib.hash import bcrypt
from uuid import UUID

import datetime
import logging
import jwt

logger: logging.Logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db_session: AsyncSession, user_context: UserContext):
        self.db_session = db_session
        self.user_context = user_context


    async def create_token(self, user: User) -> str:
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=TOKEN_TTL)
        payload = {
            "sub": user.id,
            "exp": expiration_time,
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "username": user.profile.username,
            "user_role": user.role,
            "user_status": user.status
        }
        token = jwt.encode(payload, TOKEN_SECRET, algorithm="HS256")
        return token

    async def decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, TOKEN_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Token is invalid")


    async def register_user(self, user_register_dto: UserRegistrationDTO) -> UserResponseDTO:
        user_query = select(User).where(User.email == user_register_dto.email).options(joinedload(User.profile))
        user_result = await self.db_session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user:
            raise ConflictException("User with such email has already exist.")

        try:
            user_profile_entity = UserProfile(
                username=user_register_dto.username,
            )
            user_entity = User(
                password=bcrypt.hash(user_register_dto.password),
                email=user_register_dto.email,
                profile_id=user_profile_entity.id,
                status=UserStatus.ACTIVE.value
            )
            user_entity.profile = user_profile_entity

            await self.db_session.commit()
            await self.db_session.refresh(user_entity)

            return UserResponseDTO.from_entity(user_entity)
        except IntegrityError as e:
            raise ConflictException("This user data ruins some constrains") from e
 
    async def auth_user(self, user_auth_dto: UserAuthDTO) -> UserResponseDTO:
        user_query = select(User).where(User.email == user_auth_dto.email).options(joinedload(User.profile))
        user_result = await self.db_session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise NotFoundException("Cannot find user with such email.")

        if bcrypt.verify(user_auth_dto.password, user.password):
            raise UnauthorizedException("Invalid email or password.")

        return UserResponseDTO.from_entity(user)
