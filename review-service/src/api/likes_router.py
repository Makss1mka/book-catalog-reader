from src.models.enums import UserRole, ResponseStatus, ResponseDataType
from src.middlewares.access_control import require_access
from src.models.response_dtos import CommonResponseModel
from src.annotations import DatabaseSession, UserContext
from src.services.like_service import LikeService
from fastapi.responses import JSONResponse

from fastapi import APIRouter, Request
import logging
import uuid

logger = logging.getLogger(__name__)
likes_router = APIRouter(prefix="/reviews/likes", tags=["Likes CRUD"])


@likes_router.post("/{review_id}", response_class=JSONResponse, status_code=201)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def add_like(
    request: Request,
    review_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    like_service = LikeService(db, user_context)
    await like_service.add_like(review_id)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.STRING,
        data="Like added successfully"
    )


@likes_router.delete("/{review_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def delete_like(
    request: Request,
    review_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    like_service = LikeService(db, user_context)
    await like_service.delete_like(review_id)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.STRING,
        data="Like deleted successfully"
    )
