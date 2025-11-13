from enum import Enum

class UserRole(str, Enum):
    GUEST = "GUEST"
    USER = "USER"
    ADMIN = "ADMIN"

class UserStatus(str, Enum):
    BLOCKED = "BLOCKED"
    ACTIVE = "ACTIVE"

class ResponseStatus(str, Enum):
    SUCCESS = "success"
    EXCEPTION = "exception"

class ResponseDataType(str, Enum):
    STRING = "str"
    JSON = "json"
