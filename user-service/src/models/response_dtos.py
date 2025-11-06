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


class UserAuthResponseDTO(BaseModel):
    access_token: str
    refresh_token: str
    user_data: UserResponseDTO

    @classmethod
    def from_data(cls, access_token: str, refresh_token: str, user: User) -> 'UserAuthResponseDTO':
        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            user_data=UserResponseDTO.from_entity(user)
        )


class AccessTokenResponseDTO(BaseModel):
    access_token: str
 
    @classmethod
    def from_entity(cls, access_token: str) -> 'AccessTokenResponseDTO':
        return cls(access_token=access_token)


class StatusUpdateResponseDTO(BaseModel):
    id: str
    old_status: str
    new_status: str
    message: str

