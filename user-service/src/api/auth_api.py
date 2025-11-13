from src.models.enums import ResponseDataType, ResponseStatus
from src.models.request_dtos import RefreshTokenDTO, UserRegistrationDTO, UserLoginDTO
from src.models.response_dtos import CommonResponseModel
from src.services.auth_service import AuthService
from src.annotations import DatabaseSession, UserContext, RedisClient 
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
import logging

logger: logging.Logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/users", tags=["Auth"])


@auth_router.post("/register", response_class=JSONResponse, status_code=200)
async def register(
    user_reg_dto: UserRegistrationDTO,
    db: DatabaseSession,
):
    auth_service = AuthService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await auth_service.register(user_reg_dto),
    )


@auth_router.post("/login", response_class=JSONResponse, status_code=200)
async def login(
    user_login_dto: UserLoginDTO,
    db: DatabaseSession,
):
    auth_service = AuthService(db)
    
    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await auth_service.login(user_login_dto),
    )


@auth_router.post("/refresh", response_class=JSONResponse, status_code=200)
async def refresh(
    refresh_token_dto: RefreshTokenDTO,
    db: DatabaseSession,
):
    auth_service = AuthService(db)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await auth_service.refresh(refresh_token_dto),
    )
