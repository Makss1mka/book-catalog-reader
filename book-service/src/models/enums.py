from enum import Enum

class UserRole(str, Enum):
    GUEST = "Guest"
    USER = "User"
    ADMIN = "Admin"

class UserStatus(str, Enum):
    BLOCKED = "BLOCKED"
    ACTIVE = "ACTIVE"

class BookStatus(str, Enum):
    ON_MODERATE = "ON_MODERATE"
    ACTIVE = "ACTIVE"
    PRIVATE = "PRIVATE"
    BLOCKED = "BLOCKED"
    ON_APILATION = "ON_APILATION"

class AuthorProfileStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PRIVATE = "PRIVATE"
    BLOCKED = "BLOCKED"
    ON_APILATION = "ON_APILATION"
