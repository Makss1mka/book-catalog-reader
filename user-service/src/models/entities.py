from sqlalchemy import Column, UUID, DateTime, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import uuid

class Base(DeclarativeBase):
    pass

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    profile_picture = Column(String)

    user = relationship(
        "User",
        back_populates="profile",
        uselist=False
    )
    
class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    profile_id = Column(UUID, ForeignKey('user_profiles.id'), nullable=False)
    status = Column(String, nullable=False, default='ACTIVE')
    role = Column(String, nullable=False, default='USER')
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    blocked_for = Column(DateTime, nullable=True)

    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True
    )