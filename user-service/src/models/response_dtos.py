from src.models.entities import User
from pydantic import BaseModel
from typing import Optional


class UserResponseDTO(BaseModel):
    id: str
    username: str
    email: str
    created_at: str
    profile_picture: Optional[str]
    
    @classmethod
    def from_entity(cls, entity: User) -> 'UserResponseDTO':
        return cls(
            id=str(entity.id),
            username=entity.username,
            email=entity.email,
            created_at=str(entity.created_at),
            profile_picture=entity.profile_picture if entity.profile_picture else None
        )


class StatusUpdateResponseDTO(BaseModel):
    id: str
    old_status: str
    new_status: str
    message: str

