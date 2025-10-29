from sqlalchemy import Column, UUID, DateTime, String, Float, Integer, Date, ARRAY, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import uuid


class Base(DeclarativeBase):
    pass


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(UUID, primary_key=True, default=uuid.uuid4, server_default=text('gen_random_uuid()'))
    username = Column(String, nullable=False)
    profile_picture = Column(String)

    user = relationship("User", back_populates="profile", uselist=False)
    author_profile = relationship("AuthorProfile", back_populates="user_profile", uselist=False)
    reviews = relationship("Review", back_populates="user_profile")
    liked_books = relationship("Book", secondary="book_likes", back_populates="likers")
    liked_reviews = relationship("Review", secondary="review_likes", back_populates="likers")
    book_statuses = relationship("UserBookStatus", back_populates="user_profile")

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True, default=uuid.uuid4, server_default=text('gen_random_uuid()'))
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    profile_id = Column(UUID, ForeignKey('user_profiles.id'), nullable=False)
    status = Column(String, nullable=False, default='ACTIVE', server_default=text("'ACTIVE'"))
    role = Column(String, nullable=False, default='USER', server_default=text("'USER'"))
    created_at = Column(DateTime, nullable=False, default=datetime.now, server_default=text('NOW()'))
    blocked_for = Column(DateTime, nullable=True)

    profile = relationship("UserProfile", back_populates="user")

class AuthorProfile(Base):
    __tablename__ = 'author_profiles'

    id = Column(UUID, primary_key=True, default=uuid.uuid4, server_default=text('gen_random_uuid()'))
    user_profile_id = Column(UUID, ForeignKey('user_profiles.id'), nullable=False)
    name = Column(String, nullable=False)
    rating = Column(Float, default=0.0, server_default=text('0.0'))
    common_genres = Column(ARRAY(String))
    books_count = Column(Integer, default=0, server_default=text('0'))
    reviews_count = Column(Integer, default=0, server_default=text('0'))
    likes_count = Column(Integer, default=0, server_default=text('0'))
    status = Column(String, nullable=False, default='ACTIVE', server_default=text("'ACTIVE'"))

    user_profile = relationship("UserProfile", back_populates="author_profile")
    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = 'books'

    id = Column(UUID, primary_key=True, default=uuid.uuid4, server_default=text('gen_random_uuid()'))
    author_id = Column(UUID, ForeignKey('author_profiles.id'), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    file_path = Column(String)
    cover_path = Column(String)
    genres = Column(ARRAY(String))
    added_date = Column(Date)
    status = Column(String, nullable=False, default='ON_MODERATE', server_default=text("'ON_MODERATE'"))
    total_rating = Column(Float, default=0.0, server_default=text('0.0'))
    likes_count = Column(Integer, default=0, server_default=text('0'))
    pages_count = Column(Integer, default=0, server_default=text('0'))
    reviews_count = Column(Integer, default=0, server_default=text('0'))

    author = relationship("AuthorProfile", back_populates="books")
    reviews = relationship("Review", back_populates="book")
    likers = relationship("UserProfile", secondary="book_likes", back_populates="liked_books")
    book_statuses = relationship("UserBookStatus", back_populates="book")

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(UUID, primary_key=True, default=uuid.uuid4, server_default=text('gen_random_uuid()'))
    book_id = Column(UUID, ForeignKey('books.id'), nullable=False)
    user_profile_id = Column(UUID, ForeignKey('user_profiles.id'), nullable=False)
    text = Column(String, nullable=False)
    rating = Column(Integer, nullable=False, default=0)

    book = relationship("Book", back_populates="reviews")
    user_profile = relationship("UserProfile", back_populates="reviews")
    likers = relationship("UserProfile", secondary="review_likes", back_populates="liked_reviews")

class UserBookStatus(Base):
    __tablename__ = 'user_book_statuses'

    book_id = Column(UUID, ForeignKey('books.id'), primary_key=True)
    user_profile_id = Column(UUID, ForeignKey('user_profiles.id'), primary_key=True)
    status = Column(String, nullable=False)

    book = relationship("Book", back_populates="book_statuses")
    user_profile = relationship("UserProfile", back_populates="book_statuses")

class BookLike(Base):
    __tablename__ = 'book_likes'

    book_id = Column(UUID, ForeignKey('books.id'), primary_key=True)
    user_profile_id = Column(UUID, ForeignKey('user_profiles.id'), primary_key=True)

class ReviewLike(Base):
    __tablename__ = 'review_likes'

    review_id = Column(UUID, ForeignKey('reviews.id'), primary_key=True)
    user_profile_id = Column(UUID, ForeignKey('user_profiles.id'), primary_key=True)

