from src.models.enums import UserStatus
from pydantic import BaseModel
import json

class UserSession(BaseModel):
    user_id: str
    user_role: str
    user_name: str
    user_status: str
    user_blocked_for: str

    @classmethod
    def from_json(cls, user_session_data: str) -> 'UserSession':
        user_dict_data = json.loads(user_session_data)

        return cls(
            user_id = user_dict_data["user_id"],
            user_role = user_dict_data["user_role"],
            user_name = user_dict_data["user_name"],
            user_status = user_dict_data["user_status"],
            user_blocked_for = user_dict_data["user_blocked_for"]
        )

    def to_json(self) -> dict:
        return json.dumps({
            "user_id": self.user_id,
            "user_role": self.user_role,
            "user_name": self.user_name,
            "user_status": self.user_status,
            "user_blocked_for": self.user_blocked_for
        })
