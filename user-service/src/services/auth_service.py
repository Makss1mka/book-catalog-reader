from src.models.enums import UserStatus
from src.models.request_dtos import UserRegistrationDTO, UserLoginDTO, RefreshTokenDTO
from src.models.response_dtos import UserAuthResponseDTO, AccessTokenResponseDTO
from src.middlewares.auth_middleware import UserContext
from src.models.entities import User
from src.globals import (
    ACCESS_TOKEN_SECRET, ACCESS_TOKEN_TTL, 
    REFRESH_TOKEN_SECRET, REFRESH_TOKEN_TTL
)
from src.exceptions.code_exceptions import (
    NotFoundException, ConflictException, UnauthorizedException,
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import datetime
import logging
import bcrypt
import jwt

logger: logging.Logger = logging.getLogger(__name__)

TokenStr = str
SessionIdStr = str


class AuthService:
    def __init__(self, db_session: AsyncSession, user_context: UserContext):
        self.db_session = db_session
        self.user_context = user_context


    def _create_access_token(self, user: User) -> str:
        payload = {
            "sub": str(user.id),
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=ACCESS_TOKEN_TTL),
            "iat": datetime.datetime.now(datetime.timezone.utc),
            "name": user.username,
            "role": user.role,
            "status": user.status,
            "blocked_for": str(user.blocked_for),
        }
        token = jwt.encode(payload, ACCESS_TOKEN_SECRET, algorithm="HS256")
        return token

    def _create_refresh_token(self, user: User) -> str:
        payload = {
            "sub": str(user.id),
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=REFRESH_TOKEN_TTL),
            "iat": datetime.datetime.now(datetime.timezone.utc)
        }
        token = jwt.encode(payload, REFRESH_TOKEN_SECRET, algorithm="HS256")
        return token

    def _decode_refresh_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise UnauthorizedException("Refresh token is invalid")


    async def register(self, user_register_dto: UserRegistrationDTO) -> UserAuthResponseDTO:
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

            refresh_token = self._create_refresh_token(user)
            access_token = self._create_access_token(user)
            
            return_dto = UserAuthResponseDTO(access_token, refresh_token, user)

            await self.db_session.commit()

            return return_dto
        except IntegrityError as e:
            raise ConflictException("This user data ruins some constrains") from e
 

    async def login(self, user_login_dto: UserLoginDTO) -> UserAuthResponseDTO:
        user_query = select(User).where(User.email == user_login_dto.email)
        user_result = await self.db_session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise NotFoundException("Cannot find user with such email.")

        if not bcrypt.checkpw(
            user_login_dto.password.encode('utf-8'), 
            user.password.encode('utf-8')
        ):
            raise UnauthorizedException("Invalid password.")

        return UserAuthResponseDTO(
            self._create_refresh_token(user),
            self._create_access_token(user),
            user
        )


    async def refresh(self, refresh_token_dto: RefreshTokenDTO) -> AccessTokenResponseDTO:
        user_payload = self._decode_token(refresh_token_dto.refresh_token)
        user_id = user_payload["sub"]

        user_query = select(User).where(User.id == user_id)
        user_result = await self.db_session.execute(user_query)
        user = user_result.scalar_one_or_none()

        if not user:
            raise NotFoundException("Cannot find user with such email.")

        return AccessTokenResponseDTO(
            self._create_access_token(user)
        )
