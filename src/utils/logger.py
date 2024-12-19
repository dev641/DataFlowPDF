import logging
from config.settings import LOGS_DIR
import os
import sys
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

LOGGING_LEVEL = logging.INFO  # Set your desired logging level here


class ColorFormatter(logging.Formatter):
    """Custom formatter to add colors to terminal output based on logging level."""

    COLOR_MAP = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.GREEN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
    }

    def format(self, record):
        # Add color to the log level name
        color = self.COLOR_MAP.get(record.levelno, "")
        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logger(name: str, log_file: str = f'{LOGS_DIR}/app.log'):
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    logger = logging.getLogger(name)
    logger.setLevel(
        LOGGING_LEVEL
    )  # Set logger level to the global logging level

    # FileHandler with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(LOGGING_LEVEL)  # Use the same global logging level
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # StreamHandler with colored output for stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(LOGGING_LEVEL)  # Use the same global logging level
    stream_formatter = ColorFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    stream_handler.setFormatter(stream_formatter)
    stream_handler.stream = open(
        sys.stdout.fileno(), mode='w', encoding='utf-8', closefd=False
    )

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
