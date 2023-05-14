"""
A logger
"""

import logging
import os
import sys
from logging import handlers
from pathlib import Path

from app.config import settings

FORMATTER = logging.Formatter(
    "%(asctime)-25s %(levelname)-10s %(module)-25s %(funcName)-20s %(message)s"
)


def get_console_log_handler() -> logging.StreamHandler:
    console_log_handler = logging.StreamHandler(sys.stderr)
    console_log_handler.setFormatter(FORMATTER)
    # The errors only
    console_log_handler.setLevel(logging.WARNING)
    return console_log_handler


def get_file_log_handler(path: str) -> handlers.TimedRotatingFileHandler:
    logs_dir = Path(settings.LOGS_DIR)
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
    logs_path = Path(path)
    if not logs_path.exists():
        logs_path.touch()
    file_log_handler = handlers.TimedRotatingFileHandler(
        filename=path,
        encoding="UTF-8",
        backupCount=settings.LOGS_BACKUP_DAYS,
        when="midnight",
    )
    file_log_handler.setFormatter(FORMATTER)
    file_log_handler.setLevel(logging.INFO)
    return file_log_handler


def get_logger(name: str, path: str) -> logging.Logger:
    logger = logging.getLogger(name=name)
    logger.addHandler(get_console_log_handler())
    logger.addHandler(get_file_log_handler(path=path))
    logger.setLevel(logging.INFO)
    return logger


def create_logs_path(directory: str) -> str:
    paths = directory.split("/")
    path = "/"
    for _path in paths:
        path = os.path.join(path, _path)
        if path and not os.path.exists(path):
            os.mkdir(path)
    return directory
