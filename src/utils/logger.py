# src/utils/logger.py

import logging
import sys
import os  # Import os module
from logging.handlers import RotatingFileHandler
from src.config import LOG_FILE_PATH, DEFAULT_LOG_LEVEL
from colorama import Fore, Style, init

init(autoreset=True)  # Initialize colorama

class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels."""

    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, Fore.WHITE)
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"

def setup_logger(name, log_to_console=True, log_to_file=True, level=DEFAULT_LOG_LEVEL):
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False  # Prevent duplicate log messages

    formatter = ColorFormatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    if log_to_console:
        # Redirect log messages to stderr
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_to_file:
        # Ensure the directory for the log file exists
        log_dir = os.path.dirname(LOG_FILE_PATH)
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            print(f"Failed to create log directory '{log_dir}': {e}", file=sys.stderr)
            sys.exit(1)  # Exit if the log directory cannot be created

        file_handler = RotatingFileHandler(LOG_FILE_PATH, maxBytes=5*1024*1024, backupCount=2)
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger