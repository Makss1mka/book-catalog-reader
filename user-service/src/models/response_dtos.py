import logging
from pydantic import BaseModel
from typing import Optional
from src.models.entities import User, UserProfile

logger = logging.getLogger(__name__)


class UserProfileResponseDTO(BaseModel):
    id: str
    username: str
    profile_picture: str
    
    @classmethod
    def from_entity(cls, entity: UserProfile) -> 'UserProfileResponseDTO':
        return cls(
            id=str(entity.id),
            username=entity.username,
            profile_picture=entity.profile_picture
        )


class UserResponseDTO(BaseModel):
    id: str
    title: str
    email: str
    status: str
    created_at: str
    profile_id: str
    user_profile: Optional[UserProfileResponseDTO]
    
    @classmethod
    def from_entity(cls, entity: User, include_profile: bool = False) -> 'UserResponseDTO':
        return cls(
            id=str(entity.id),
            email=entity.email,
            status=entity.status,
            created_at=str(entity.created_at),
            profile_id=str(entity.profile_id),
            user_profile=UserProfileResponseDTO.from_entity(entity.profile) if include_profile and entity.profile else None
        )


class StatusUpdateResponseDTO(BaseModel):
    id: str
    old_status: str
    new_status: str
    message: str

