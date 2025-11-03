from src.models.enums import UserStatus, UserRole
from src.models.response_dtos import UserResponseDTO
from src.models.request_dtos import UserRegistrationDTO, UserAuthDTO
from src.middlewares.auth_middleware import UserContext
from src.models.entities import User
from src.globals import TOKEN_SECRET, TOKEN_TTL, REDIS_SESSION_TTL
from src.exceptions.code_exceptions import (
    NotFoundException, ConflictException, UnauthorizedException,
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from redis.asyncio import Redis
from sqlalchemy import select

import datetime
import logging
import bcrypt
import uuid
import json
import jwt

logger: logging.Logger = logging.getLogger(__name__)

TokenStr = str
SessionIdStr = str


class AuthService:
    def __init__(self, db_session: AsyncSession, user_context: UserContext):
        self.db_session = db_session
        self.user_context = user_context


    def _create_token(self, user: User) -> str:
        payload = {
            "sub": str(user.id),
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=TOKEN_TTL),
            "iat": datetime.datetime.now(datetime.timezone.utc)
        }
        token = jwt.encode(payload, TOKEN_SECRET, algorithm="HS256")
        return token

    def _decode_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, TOKEN_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Token is invalid")

    async def _create_session(self, user: User, redis: Redis) -> str:
        user_payload = {
            "user-id": str(user.id),
            "user-name": user.username,
            "user-role": user.role,
            "user-status": user.status
        }

        if user_payload.get("user-status", "") == UserStatus.BLOCKED.value:
            user_payload["user-blocked_for"] = user.blocked_for

        session_id = str(uuid.uuid4())

        await redis.set(session_id, json.dumps(user_payload), REDIS_SESSION_TTL)

        return session_id


    async def register_user(self, user_register_dto: UserRegistrationDTO, redis: Redis) -> tuple[UserResponseDTO, TokenStr, SessionIdStr]:
        similar_user_query = select(User).where(User.email == user_register_dto.email)
        similar_user_result = await self.db_session.execute(similar_user_query)
        similar_user = similar_user_result.scalar_one_or_none()

        if similar_user:
            raise ConflictException("User with such email has already exist.")

        try:
            salt = bcrypt.gensalt(rounds=12)
            hashed_pass = bcrypt.hashpw(user_register_dto.password.encode('utf-8'), salt).decode('utf-8')

            user = User(
                password=hashed_pass,
                username=user_register_dto.username,
                email=user_register_dto.email,
                status=UserStatus.ACTIVE.value,
            )

            self.db_session.add(user)

            await self.db_session.flush()

            return_dto = UserResponseDTO.from_entity(user)
            refresh_token = self._create_token(user)
            session_id = await self._create_session(user, redis)

            await self.db_session.commit()

            return (return_dto, refresh_token, session_id)
        except IntegrityError as e:
            raise ConflictException("This user data ruins some constrains") from e
 

    async def auth_user(self, user_auth_dto: UserAuthDTO, redis: Redis) -> tuple[UserResponseDTO, TokenStr, SessionIdStr]:
        user_query = select(User).where(User.email == user_auth_dto.email)
        user_result = await self.db_session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise NotFoundException("Cannot find user with such email.")

        if not bcrypt.checkpw(
            user_auth_dto.password.encode('utf-8'), 
            user.password.encode('utf-8')
        ):
            raise UnauthorizedException("Invalid password.")

        return (
            UserResponseDTO.from_entity(user),
            self._create_token(user),
            await self._create_session(user, redis)
        )


    async def auth_via_token(self, token: str, redis: Redis) -> tuple[UserResponseDTO, TokenStr, SessionIdStr]:
        user_payload = self._decode_token(token)
        user_id = user_payload["sub"]

        user_query = select(User).where(User.id == user_id)
        user_result = await self.db_session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise NotFoundException("Cannot find user with such email.")

        return (
            UserResponseDTO.from_entity(user),
            self._create_token(user),
            await self._create_session(user, redis)
        )
