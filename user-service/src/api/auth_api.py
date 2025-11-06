from src.models.request_dtos import RefreshTokenDTO, UserRegistrationDTO, UserLoginDTO
from src.models.response_dtos import UserAuthResponseDTO, AccessTokenResponseDTO
from src.services.auth_service import AuthService
from src.annotations import DatabaseSession, UserContext, RedisClient 
from fastapi import APIRouter, Request, Response
import logging

logger: logging.Logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/users", tags=["Auth"])


@auth_router.post("/register", response_model=UserAuthResponseDTO)
async def register(
    request: Request,
    response: Response,
    user_reg_dto: UserRegistrationDTO,
    db: DatabaseSession,
    user_context: UserContext,
    redis: RedisClient 
) -> UserAuthResponseDTO:
    auth_service = AuthService(db)
    return await auth_service.register(user_reg_dto) 


@auth_router.post("/login", response_model=UserAuthResponseDTO)
async def login(
    user_login_dto: UserLoginDTO,
    db: DatabaseSession,
) -> UserAuthResponseDTO:
    auth_service = AuthService(db)
    return await auth_service.login(user_login_dto)


@auth_router.post("/refresh", response_model=AccessTokenResponseDTO)
async def refresh(
    refresh_token_dto: RefreshTokenDTO,
    db: DatabaseSession,
) -> AccessTokenResponseDTO:
    auth_service = AuthService(db)
    return await auth_service.refresh(refresh_token_dto)
