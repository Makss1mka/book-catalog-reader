from enum import Enum

class UserRole(str, Enum):
    GUEST = "GUEST"
    USER = "USER"
    ADMIN = "ADMIN"

class UserStatus(str, Enum):
    BLOCKED = "BLOCKED"
    ACTIVE = "ACTIVE"

class BookStatus(str, Enum):
    WAIT_FILE = "WAIT_FILE"
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

class UserBookStatusEnum(str, Enum):
    READ = "READ"
    READING = "READING"
    DROP = "DROP"
    LIKED = "LIKED"
