from sqlalchemy import Column, UUID, DateTime, String
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import uuid

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    profile_picture = Column(String)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    status = Column(String, nullable=False, default='ACTIVE')
    role = Column(String, nullable=False, default='USER')
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    blocked_for = Column(DateTime, nullable=True)
