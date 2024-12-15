from config.config_loader import load_json
import re
from utils.logger import setup_logger

log = setup_logger(__name__)


def correct_misspelled_word(filePath):
    log.info(f"Initializing misspelled word correction with file: {filePath}")

    def decorator(func):
        log.debug("Setting up correction decorator")

        def wrapper(data, *args, **kwargs):
            log.debug(
                f"Starting word correction for data: {data[:100]}..."
            )  # Log first 100 chars

            ocr_corrections = load_json(filePath=filePath)
            log.debug(f"Loaded {len(ocr_corrections)} correction patterns")

            for key, val in ocr_corrections.items():
                for item in val:
                    data = data.replace(item, key)

            log.debug("Word corrections applied")
            return func(data, *args, **kwargs)

        return wrapper

    return decorator


def normalize_text(func):
    log.debug("Setting up text normalization decorator")

    def wrapper(data, *args, **kwargs):
        log.debug(
            f"Starting text normalization for data: {data[:100]}..."
        )  # Log first 100 chars

        data = (
            data.replace(" : ", ":")
            .replace(": ", ":")
            .replace("::", ":")
            .split("\n")
        )
        log.debug("Text normalization completed")

        return func(data, *args, **kwargs)

    return wrapper


def hindi_to_english_digits(filePath):
    log.info(
        f"Initializing Hindi to English digit conversion with file: {filePath}"
    )

    def decorator(func):
        log.debug("Setting up digit conversion decorator")

        def wrapper(data, *args, **kwargs):
            log.debug(
                f"Starting digit conversion for data: {data[:100]}..."
            )  # Log first 100 chars

            hindi_to_english_digits = load_json(filePath=filePath)
            log.debug(f"Loaded {len(hindi_to_english_digits)} digit mappings")

            data = ''.join(hindi_to_english_digits.get(ch, ch) for ch in data)
            log.debug("Digit conversion completed")

            return func(data, *args, **kwargs)

        return wrapper

    return decorator


def clean_empty_lines(func):
    log.debug("Setting up empty line cleaning decorator")

    def wrapper(data, *args, **kwargs):
        log.debug(
            f"Starting empty line cleaning for data: {data[:100]}..."
        )  # Log first 100 chars
        data = [line.strip() for line in data.split("\n") if line.strip()]
        log.debug(f"Cleaned {len(data)} non-empty lines")
        return func("\n".join(data), *args, **kwargs)

    return wrapper


def format_pattern(pattern, replacement):
    log.info(f"Initializing pattern formatting with pattern: {pattern}")

    def decorator(func):
        log.debug("Setting up pattern formatting decorator")

        def wrapper(data, *args, **kwargs):
            log.debug(
                f"Starting pattern formatting for data: {data[:100]}..."
            )  # Log first 100 chars
            data = re.sub(pattern=pattern, repl=replacement, string=data)
            log.debug("Pattern formatting completed")
            return func(data, *args, **kwargs)

        return wrapper

    return decorator
