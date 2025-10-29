from dotenv import load_dotenv
import logging
import os

load_dotenv()

#
# App start params
#
APP_HOST: str = os.environ.get("APP_HOST", )
APP_PORT: int = int(os.environ.get("APP_PORT"))

#
# Database credits
#
DB_USER: str = os.environ.get("DB_USER")
DB_PASSWORD: str = os.environ.get("DB_PASSWORD")
DB_NAME: str = os.environ.get("DB_NAME")
DB_HOST: str = os.environ.get("DB_HOST")
DB_URL: str = os.environ.get("DB_URL")
DB_ECHO_MODE: bool = bool(os.environ.get("DB_ECHO_MODE", "False"))

#
# Logging config
#
LOGS_LEVEL: int = logging.DEBUG
LOGS_FILENAME: str = "logs/{date}.log"
LOGS_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

#
# File upload configs
#
MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
ALLOWED_FILE_TYPES: list = ["application/pdf"]
UPLOAD_DIR: str = "uploads/profiles"

#
# Pagination configs
#
DEFAULT_PAGE_SIZE: int = 10
MAX_PAGE_SIZE: int = 100
MAX_PAGE_SIZE_NON_ADMIN: int = 20

#
# Search configs
#
MAX_GENRES_PER_BOOK: int = 10
MAX_SEARCH_RESULTS: int = 1000

#
# Other file vars
#
MAX_PAGES_PER_REQUEST: int = 10

#
# Token configs
#
TOKEN_SECRET: str = os.environ.get("TOKEN_SECRET")
TOKEN_TTL: int = 30 * 60 * 60
