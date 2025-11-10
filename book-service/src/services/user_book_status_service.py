from src.models.crud_request_dtos import UserBookStatusCreateDTO, UserBookReadingStatusEndPageUpdateDTO, UserBookStatusUpdateDTO
from src.models.response_dtos import UserBookStatusListResponseDTO, UserBookStatusResponseDTO
from src.exceptions.code_exceptions import BadRequestException, ForbiddenException, NoContentException, NotFoundException, ConflictException
from src.middlewares.auth_middleware import UserContext
from src.models.entities import Book, UserBookStatus
from src.models.enums import UserBookStatusEnum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, desc, func
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class UserBookStatusService:
    def __init__(self, db_session: AsyncSession, user_context: UserContext):
        self._db_session = db_session
        self._user_context = user_context
    
    
    async def add_status(self, book_id: uuid.UUID, create_status_dto: UserBookStatusCreateDTO) -> None:
        book_query = select(Book).where(Book.id == book_id)
        book_result = await self._db_session.execute(book_query)
        book = book_result.scalar_one_or_none()
        
        if not book:
            raise NotFoundException("Book not found")
        
        book_status = UserBookStatus(
            book_id=book_id,
            user_id=self._user_context.user_id,
            added_date=datetime.now(),
            status=create_status_dto.status.value,
        )
        
        try:
            self._db_session.add(book_status)
            await self._db_session.commit()
        except Exception as e:
            logger.exception(e)
            raise ConflictException("Cannot add status cause of some conflicts or ruins of rules")
    
    async def update_status(self, book_id: uuid.UUID, update_status_dto: UserBookStatusUpdateDTO) -> None:
        status_query = select(UserBookStatus).where(and_(UserBookStatus.book_id == book_id, UserBookStatus.user_id == self._user_context.user_id))
        status_result = await self._db_session.execute(status_query)
        status = status_result.scalar_one_or_none()
        
        if not status:
            raise NotFoundException("Statused not setted to this book")
        
        if (
            not self._user_context.is_admin
            and self._user_context.user_id != status.user_id
        ):
            raise ForbiddenException("You don't have permission to modify this status")
        
        is_smth_changed = False
        if update_status_dto.status is not None:
            status.status = update_status_dto.status.value
            status.end_page = -1
            is_smth_changed = True
        
        if is_smth_changed:
            try:
                await self._db_session.commit()
            except Exception as e:
                logger.exception(e)
                raise ConflictException("Cannot update status cause of some conflicts or ruins of rules")
        else:
            raise NoContentException("Nothing changed")
    
    async def delete_status(self, book_id: uuid.UUID) -> None:
        status_query = select(UserBookStatus).where(and_(UserBookStatus.book_id == book_id, UserBookStatus.user_id == self._user_context.user_id))
        status_result = await self._db_session.execute(status_query)
        status = status_result.scalar_one_or_none()
        
        if not status:
            raise NotFoundException("Statused not setted to this book")
        
        if (
            not self._user_context.is_admin
            and self._user_context.user_id != status.user_id
        ):
            raise ForbiddenException("You don't have permission to modify this status")
        
        await self._db_session.delete(status)
        await self._db_session.commit()


    async def update_end_page(self, book_id: uuid.UUID, update_end_page: UserBookReadingStatusEndPageUpdateDTO) -> None:
        status_query = select(UserBookStatus).where(and_(UserBookStatus.book_id == book_id, UserBookStatus.user_id == self._user_context.user_id))
        status_result = await self._db_session.execute(status_query)
        status = status_result.scalar_one_or_none()
        
        if not status:
            raise NotFoundException("Statused not setted to this book")
        
        if (
            not self._user_context.is_admin
            and self._user_context.user_id != status.user_id
        ):
            raise ForbiddenException("You don't have permission to modify this status")
        
        if status.status != UserBookStatusEnum.READING.value:
            raise NoContentException("Cannot change end page, cause book is not in rigth user status")
        
        try:
            status.end_page = update_end_page.end_page
            await self._db_session.commit()
        except Exception as e:
            logger.exception(e)
            raise ConflictException("Cannot update status cause of some conflicts or ruins of rules")


    async def get_statused_books(self, status: UserBookStatusEnum, pagination: dict) -> UserBookStatusListResponseDTO:
        if not self._user_context.is_admin and pagination["page_size"] > 20:
            raise BadRequestException("Maximum 20 pages allowed for non-admin users")

        query = select(UserBookStatus).where(
            and_(
                UserBookStatus.user_id == self._user_context.user_id,
                UserBookStatus.status == status.value
            )
        )
        query = query.order_by(desc(UserBookStatus.added_date))

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self._db_session.execute(count_query)
        total_count = count_result.scalar()
        total_pages = (total_count + pagination["page_size"] - 1) // pagination["page_size"]

        offset = (pagination["page_number"] - 1) * pagination["page_size"]
        query = query.offset(offset).limit(pagination["page_size"])
        query = query.options(selectinload(UserBookStatus.book).selectinload(Book.author))

        result = await self._db_session.execute(query)
        books = result.scalars().all()

        return UserBookStatusListResponseDTO(
            books=[UserBookStatusResponseDTO.from_entity(i) for i in books],
            total_count=total_count,
            page_number=pagination["page_number"],
            page_size=pagination["page_size"],
            total_pages=total_pages
        )

