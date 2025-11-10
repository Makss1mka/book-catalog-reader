from src.exceptions.code_exceptions import ForbiddenException, NoContentException, NotFoundException, ConflictException, BadRequestException
from src.models.response_dtos import ReviewResponseDTO, ReviewsListResponseDTO
from src.models.crud_request_dtos import ReviewCreateDTO, ReviewUpdateDTO
from src.middlewares.auth_middleware import UserContext
from src.models.entities import Review, ReviewLike

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, desc, asc, and_
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class ReviewService:
    def __init__(self, db_session: AsyncSession, user_context: UserContext):
        self._db_session = db_session
        self._user_context = user_context
    

    def _get_sort_column(self, sort_by: str | None):
        sort_columns = {
            'rating': Review.rating,
            'added_date': Review.added_date,
        }

        if not sort_by:
            return Review.added_date
        elif sort_by in sort_columns:
            return sort_columns.get(sort_columns[sort_by])
        else:
            raise BadRequestException("Invalid parametr for sort field")

    async def get_reviews_by_book_id(self, book_id: uuid.UUID, pagination: dict) -> ReviewsListResponseDTO:
        if not self._user_context.is_admin and pagination["page_size"] > 20:
            raise BadRequestException("Maximum 20 pages allowed for non-admin users")
        
        my_review_query = select(Review).where(
            and_(
                Review.book_id == book_id,
                Review.user_id == self._user_context.user_id
            )
        )
        my_review_result = await self._db_session.execute(my_review_query)
        my_review = my_review_result.scalar_one_or_none()

        query = select(Review).where(Review.book_id == book_id)

        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self._db_session.execute(count_query)
        total_count = count_result.scalar()
        total_pages = (total_count + pagination["page_size"] - 1) // pagination["page_size"]

        sort_column = self._get_sort_column(pagination["sort_by"])

        if pagination["sort_order"] == None or pagination["sort_order"] == 'desc':
            query = query.order_by(desc(sort_column))
        elif pagination["sort_order"] == 'asc':
            query = query.order_by(asc(sort_column))
        else:
            raise BadRequestException("Invalid parametr for sort order")

        offset = (pagination["page_number"] - 1) * pagination["page_size"]
        query = query.offset(offset).limit(pagination["page_size"])
        query = query.options(selectinload(Review.likers))

        result = await self._db_session.execute(query)
        reviews = result.scalars().all()
        
        found_reviews = []
        if my_review: 
            found_reviews.append(ReviewResponseDTO.from_entity(my_review, True, self._user_context.user_id))
        for i in reviews: 
            if i.user_id == self._user_context.user_id: continue
            found_reviews.append(ReviewResponseDTO.from_entity(i, True, self._user_context.user_id))

        return ReviewsListResponseDTO(
            reviews=found_reviews,
            total_count=total_count,
            page_number=pagination["page_number"],
            page_size=pagination["page_size"],
            total_pages=total_pages
        )
    


    async def create_review(self, review_create_dto: ReviewCreateDTO) -> ReviewResponseDTO:
        review_query = select(Review).where(and_(Review.user_id == self._user_context.user_id, Review.book_id == review_create_dto.book_id))
        review_result = await self._db_session.execute(review_query)
        review = review_result.scalar_one_or_none()
        
        if review:
            raise ConflictException("Review to this book you have already do")
        
        new_review = Review(
            book_id=review_create_dto.book_id,
            user_id=self._user_context.user_id,
            user_name=self._user_context.user_name,
            text=review_create_dto.text,
            rating=review_create_dto.rating,
            added_date=datetime.now(),
        )
        
        try:
            self._db_session.add(new_review)
            await self._db_session.flush()

            new_review_dto = ReviewResponseDTO.from_entity(new_review)

            await self._db_session.commit()

            return new_review_dto
        except Exception as e:
            logger.exception(e)
            raise ConflictException("Cannot create review cause of some conflicts or ruins of rules")
    
    async def update_review(self, review_id: uuid.UUID, review_update_dto: ReviewUpdateDTO) -> ReviewResponseDTO:
        review_query = select(Review).where(Review.id == review_id)
        review_result = await self._db_session.execute(review_query)
        review = review_result.scalar_one_or_none()
        
        if not review:
            raise NotFoundException("Review_ not found")
        
        if (
            not self._user_context.is_admin
            and self._user_context.user_id != review.user_id
        ):
            raise ForbiddenException("You don't have permission to modify this review")
        
        is_smth_changed = False
        if review_update_dto.text is not None:
            review.text = review_update_dto.text
            is_smth_changed = True
        if review_update_dto.rating is not None:
            review.rating = review_update_dto.rating
            is_smth_changed = True
        
        if is_smth_changed:
            try:
                await self._db_session.flush()

                updated_review_dto = ReviewResponseDTO.from_entity(review)

                await self._db_session.commit()

                return updated_review_dto
            except Exception as e:
                logger.exception(e)
                raise ConflictException("Cannot add status cause of some conflicts or ruins of rules")
        else:
            raise NoContentException("Nothing changed")
    
    async def delete_review(self, review_id: uuid.UUID) -> None:
        review_query = select(Review).where(Review.id == review_id)
        review_result = await self._db_session.execute(review_query)
        review = review_result.scalar_one_or_none()
        
        if not review:
            raise NotFoundException("Review_ not found")
        
        if (
            not self._user_context.is_admin
            and self._user_context.user_id != review.user_id
        ):
            raise ConflictException("You don't have permission to modify this review")

        await self._db_session.delete(review)
        await self._db_session.commit()
        
    