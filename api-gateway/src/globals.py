from dotenv import load_dotenv
import logging
import os

load_dotenv()

#
# App start params
#
APP_HOST: str = os.environ.get("APP_HOST", )
APP_PORT: int = int(os.environ.get("APP_PORT"))
STARTUP_PROFILE: str = "dev"

#
# Logging config
#
LOGS_LEVEL: int = logging.DEBUG
LOGS_FILENAME: str = "logs/{date}.log"
LOGS_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

#
# Redis configs
#
REDIS_HOST: str = os.environ.get("REDIS_HOST")
REDIS_PORT: int = os.environ.get("REDIS_PORT")

#
# SESSION
#
SESSION_COOKIE_NAME = "session_id"
SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 30
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTP_ONLY = True
SESSION_COOKIE_SAME_SITE = "Lax"
SESSION_CACHE_TTL = 60 * 5

#
# ROUTING
#
AUTH_FREE_PATHS = {
    "user-service": "/users/register",
    "user-service": "/users/auth",
    "user-service": "/users/refresh",
}
SERVICES_URLS = {
    "user-service": "http://user-service:8083",
    "book-service": "http://book-service:8082"
}
STATIC_NGINX_URL = "http://static-nginx"

#
# HEADER'S NAMES
#
USER_ID_HEADER_NAME = "x-user-id"
USER_ROLE_HEADER_NAME = "x-user-role"
USER_NAME_HEADER_NAME = "x-user-name"
USER_STATUS_HEADER_NAME = "x-user-status"
USER_BLOCKED_FOR_HEADER_NAME = "x-user-blocked-for"
TRACE_ID_HEADER_NAME = "x-trace-id"
REQUEST_ID_HEADER_NAME = "request-id"

#
# Allower returning headers
#
ALLOWED_RETURNING_HEADERS = [
    "content-type", 
    "content-length",
    "location",
    "date",
    "request-id",
    "set-cookie"
]

#
# Cors configs
# 
ALLOWED_ORIGINS = ["*"]
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
ALLOWED_HEADERS = ["*"]
ALLOWED_CREDENTIALS = True

#
# Other configs
#
SERVICE_NOT_RESPONDING_TIMEOUT = 10
