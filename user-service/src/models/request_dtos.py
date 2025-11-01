from pydantic import BaseModel, Field, EmailStr
from src.models.enums import UserStatus
from typing import Optional


class UserRegistrationDTO(BaseModel):
    username: str = Field(..., min_length=3, max_length=40)
    password: str = Field(..., min_length=6, max_length=50)
    email: EmailStr


class UserAuthDTO(BaseModel):
    password: str = Field(..., min_length=6, max_length=50)
    email: EmailStr


class UserUpdateDTO(BaseModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=40)


class UserStatusUpdateDTO(BaseModel):
    status: UserStatus = Field(...)
