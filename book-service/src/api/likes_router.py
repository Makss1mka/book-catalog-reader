from src.annotations import DatabaseSession, UserContext
from src.middlewares.access_control import require_access
from src.services.likes_service import LikesService
from src.models.enums import UserRole

from fastapi import APIRouter, Request
import logging
import uuid

logger = logging.getLogger(__name__)
likes_router = APIRouter(tags=["Likes CRUD"])


@likes_router.post("/books/{book_id}/likes")
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def add_like(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    like_service = LikesService(db, user_context)
    await like_service.add_like(book_id)
    return {"message": "Like added successfully"}


@likes_router.delete("/books/{book_id}/likes")
@require_access(
    allowed_roles=[UserRole.USER, UserRole.ADMIN],
    require_authentication=True
)
async def delete_like(
    request: Request,
    book_id: uuid.UUID,
    db: DatabaseSession,
    user_context: UserContext
):
    like_service = LikesService(db, user_context)
    await like_service.delete_like(book_id)
    return {"message": "Like deleted successfully"}
