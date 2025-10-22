from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date
from src.models.enums import BookStatus, AuthorProfileStatus


class BookCreateDTO(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    genres: Optional[List[str]] = Field(default=[])
    
    @validator('genres')
    def validate_genres(cls, v):
        if v is None:
            return []
        if len(v) > 10:
            raise ValueError('Maximum 10 genres allowed')
        return [genre.strip() for genre in v if genre.strip()]


class BookUpdateDTO(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    genres: Optional[List[str]] = Field(None)
    
    @validator('genres')
    def validate_genres(cls, v):
        if v is None:
            return None
        if len(v) > 10:
            raise ValueError('Maximum 10 genres allowed')
        return [genre.strip() for genre in v if genre.strip()]


class AuthorProfileCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    common_genres: Optional[List[str]] = Field(default=[])
    
    @validator('common_genres')
    def validate_genres(cls, v):
        if v is None:
            return []
        if len(v) > 10:
            raise ValueError('Maximum 10 genres allowed')
        return [genre.strip() for genre in v if genre.strip()]


class AuthorProfileUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    common_genres: Optional[List[str]] = Field(None)
    
    @validator('common_genres')
    def validate_genres(cls, v):
        if v is None:
            return None
        if len(v) > 10:
            raise ValueError('Maximum 10 genres allowed')
        return [genre.strip() for genre in v if genre.strip()]


class BookStatusUpdateDTO(BaseModel):
    status: BookStatus = Field(...)


class AuthorProfileStatusUpdateDTO(BaseModel):
    status: AuthorProfileStatus = Field(...)
