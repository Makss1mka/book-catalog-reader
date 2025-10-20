from dotenv import load_dotenv
import logging
import os

load_dotenv()

#
# App start params
#
APP_HOST: str = os.environ.get("APP_HOST")
APP_PORT: str | int = os.environ.get("APP_PORT")

#
# Database credits
#
DB_USER: str = os.environ.get("DB_USER")
DB_PASSWORD: str = os.environ.get("DB_PASSWORD")
DB_NAME: str = os.environ.get("DB_NAME")
DB_HOST: str = os.environ.get("DB_HOST")
DB_URL: str = os.environ.get("DB_URL")

#
# Logging config
#
LOGS_LEVEL: int = logging.DEBUG
LOGS_FILENAME: str = "logs/{date}.log"
LOGS_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

#
# Routers configs
#
BOOKS_CRUD_ROUTER_PREFIX: str = "/books"
