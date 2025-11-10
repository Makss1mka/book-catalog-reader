from sqlalchemy import Column, UUID, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
import uuid

class Base(DeclarativeBase):
    pass

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID, nullable=False)
    user_id = Column(UUID, nullable=False)
    user_name = Column(String, nullable=False)
    text = Column(String, nullable=False)
    rating = Column(Integer, nullable=False, default=0)
    added_date = Column(DateTime, nullable=False)

    likers = relationship("ReviewLike", back_populates="review", cascade="all, delete-orphan")

class ReviewLike(Base):
    __tablename__ = 'review_likes'

    review_id = Column(UUID, ForeignKey('reviews.id'), primary_key=True)
    user_id = Column(UUID, primary_key=True)

    review = relationship("Review", back_populates="likers", uselist=False)
