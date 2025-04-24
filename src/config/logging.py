import logging
import os
import sys

from logging import Logger
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging() -> Logger:
    # Create logs directory if it doesn't exist
    log_file = os.getenv("LOG_FILE", "logs/app.log")
    logs_dir = Path(log_file).parent
    logs_dir.mkdir(exist_ok=True)

    # Get logging configuration from environment variables
    log_level = os.getenv("LOG_LEVEL", "DEBUG")
    max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))  # Default 10MB
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))
    console_format = os.getenv("LOG_FORMAT_CONSOLE", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_format = os.getenv(
        "LOG_FORMAT_FILE", "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create formatters
    console_formatter = logging.Formatter(console_format)
    file_formatter = logging.Formatter(file_format)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)

    # File handler
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.info("Logging configured with level %s", log_level)
    logger.debug("Log file: %s, max bytes: %d, backup count: %d", log_file, max_bytes, backup_count)

    return logger
