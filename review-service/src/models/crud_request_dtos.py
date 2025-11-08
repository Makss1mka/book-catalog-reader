from pydantic import BaseModel, Field
import uuid

class ReviewCreateDTO(BaseModel):
    book_id: uuid.UUID = Field(...)
    text: str = Field(..., min_length=1, max_length=500)
    rating: int = Field(..., ge=0, le=5)

class ReviewUpdateDTO(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)
    rating: int = Field(..., ge=0, le=5)
