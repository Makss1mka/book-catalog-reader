from sqlalchemy import Column, UUID, String, Float, Integer, Date, ARRAY, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, relationship
import uuid

class Base(DeclarativeBase):
    pass

class AuthorProfile(Base):
    __tablename__ = 'author_profiles'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_profile_id = Column(UUID, ForeignKey('user_profiles.id'), nullable=False)
    name = Column(String, nullable=False)
    rating = Column(Float, default=0.0)
    common_genres = Column(ARRAY(String))

    user_profile = relationship("UserProfile", back_populates="author_profile")
    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = 'books'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID, ForeignKey('author_profiles.id'), nullable=False)
    title = Column(String, nullable=False)
    file_path = Column(String)
    genres = Column(ARRAY(String))
    issued_date = Column(Date)
    status = Column(String, nullable=False, default='ON MODERATE')

    author = relationship("AuthorProfile", back_populates="books")
    reviews = relationship("Review", back_populates="book")
    likers = relationship("UserProfile", secondary="book_likes", back_populates="liked_books")
    book_statuses = relationship("UserBookStatus", back_populates="book")
