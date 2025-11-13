
from src.models.enums import UserRole, UserStatus, ResponseDataType, ResponseStatus
from src.models.crud_request_dtos import ReviewCreateDTO, ReviewUpdateDTO
from src.annotations import CommonParams, DatabaseSession, UserContext
from src.middlewares.access_control import require_access
from src.models.response_dtos import CommonResponseModel
from src.services.review_service import ReviewService

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
import logging
import uuid

logger = logging.getLogger(__name__)
review_crud_router = APIRouter(prefix="/reviews", tags=["Reviews CRUD"])


@review_crud_router.post("/", response_class=JSONResponse, status_code=201)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def create_review(
    request: Request,
    db: DatabaseSession,
    user_context: UserContext,
    review_data: ReviewCreateDTO
):
    review_service = ReviewService(db, user_context)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await review_service.create_review(review_data)
    )


@review_crud_router.get("/{book_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.GUEST, UserRole.USER, UserRole.ADMIN],
    require_authentication=False
)
async def get_reviews(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext,
    pagination: CommonParams
):  
    review_service = ReviewService(db, user_context)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await review_service.get_reviews_by_book_id(book_id, pagination)
    )


@review_crud_router.put("/{review_id}", response_class=JSONResponse, status_code=200)
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def update_review(
    request: Request,
    review_id: uuid.UUID,
    review_data: ReviewUpdateDTO,
    db: DatabaseSession,
    user_context: UserContext
):
    review_service = ReviewService(db, user_context)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data=await review_service.update_review(review_id, review_data)
    )


@review_crud_router.delete("/{review_id}")
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def delete_review(
    request: Request,
    review_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    review_service = ReviewService(db, user_context)
    await review_service.delete_review(review_id)

    return CommonResponseModel(
        status=ResponseStatus.SUCCESS,
        data_type=ResponseDataType.JSON,
        data="Review deleted successfully"
    )
