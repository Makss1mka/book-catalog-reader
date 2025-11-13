from sqlalchemy import Column, UUID, String, Float, Integer, DateTime, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import ARRAY
import uuid

class Base(DeclarativeBase):
    pass

class AuthorProfile(Base):
    __tablename__ = 'author_profiles'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, nullable=False)
    name = Column(String, nullable=False)
    rating = Column(Float, default=0.0)
    common_genres = Column(ARRAY(String))
    books_count = Column(Integer, default=0)
    reviews_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    status = Column(String, nullable=False, default='ACTIVE')

    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = 'books'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID, ForeignKey('author_profiles.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    file_path = Column(String)
    cover_path = Column(String)
    genres = Column(ARRAY(String))
    added_date = Column(DateTime)
    status = Column(String, nullable=False, default='ON_MODERATE')
    total_rating = Column(Float, default=0.0)
    likes_count = Column(Integer, default=0)
    pages_count = Column(Integer, default=0)
    reviews_count = Column(Integer, default=0)

    author = relationship("AuthorProfile", back_populates="books")
    likers = relationship("BookLike", back_populates="book", cascade="all, delete-orphan")
    book_statuses = relationship("UserBookStatus", back_populates="book", cascade="all, delete-orphan")

class UserBookStatus(Base):
    __tablename__ = 'user_book_statuses'

    book_id = Column(UUID, ForeignKey('books.id'), primary_key=True)
    user_id = Column(UUID, primary_key=True)
    status = Column(String, nullable=False)
    added_date = Column(DateTime, nullable=False)
    end_page = Column(Integer, nullable=False, default=1)

    book = relationship("Book", back_populates="book_statuses", uselist=False)

class BookLike(Base):
    __tablename__ = 'book_likes'

    book_id = Column(UUID, ForeignKey('books.id'), primary_key=True)
    user_id = Column(UUID, primary_key=True)

    book = relationship("Book", back_populates="likers", uselist=False)
