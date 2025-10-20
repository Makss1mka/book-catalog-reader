from logging.handlers import TimedRotatingFileHandler
from fastapi.logger import logger as fastapi_logger
from datetime import datetime
import logging
import sys
import os


def setup_logging(
        logs_level: int,
        logs_filename: str,
        logs_format: str
) -> None:
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers.clear()

    formatter = logging.Formatter(logs_format)

    # Simple console/stdout logging
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    # File logging handler
    os.makedirs("logs", exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        logs_filename.format(date=datetime.now().strftime('%Y-%m-%d')),
        when="midnight",
        interval=1,
        backupCount=7
    )
    file_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logs_level)
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)

    fastapi_logger.handlers = logger.handlers
    fastapi_logger.setLevel(logs_level)