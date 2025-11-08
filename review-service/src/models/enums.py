from enum import Enum

class UserRole(str, Enum):
    GUEST = "GUEST"
    USER = "USER"
    ADMIN = "ADMIN"

class UserStatus(str, Enum):
    BLOCKED = "BLOCKED"
    ACTIVE = "ACTIVE"

