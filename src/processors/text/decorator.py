from config.config_loader import load_json
import re
from src.utils.logger import setup_logger
from functools import wraps
from config.settings import (
    VOTER_NAME_FIELD_DETECT_PATTERN,
    MAKAN_NUMBER_FIELD_DETECT_PATTERN,
    GENDER_AGE_PATTERN,
)

log = setup_logger(__name__)


def correct_misspelled_word(filePath):
    log.info(f"Initializing misspelled word correction with file: {filePath}")

    def decorator(func):
        log.debug("Setting up correction decorator")

        @wraps(func)
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

    @wraps(func)
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

        @wraps(func)
        def wrapper(data, *args, **kwargs):
            log.debug(
                f"Starting digit conversion for data: {data[:100]}..."
            )  # Log first 100 chars

            hindi_to_english_digits = load_json(filePath=filePath)
            log.debug(f"Loaded {len(hindi_to_english_digits)} digit mappings")
            for row in data:
                for idx, element in enumerate(row):
                    # Convert Hindi digits to English digits for each element and update in-place
                    row[idx] = ''.join(
                        hindi_to_english_digits.get(ch, ch) for ch in element
                    )
            # data = ''.join(hindi_to_english_digits.get(ch, ch) for ch in data)
            log.debug("Digit conversion completed")

            return func(data, *args, **kwargs)

        return wrapper

    return decorator


def clean_empty_lines(func):
    log.debug("Setting up empty line cleaning decorator")

    @wraps(func)
    def wrapper(data, *args, **kwargs):
        log.debug(
            f"Starting empty line cleaning for data: {data[:100]}..."
        )  # Log first 100 chars
        data = [line.strip() for line in data if line.strip()]
        log.debug(f"Cleaned {len(data)} non-empty lines")
        return func("\n".join(data), *args, **kwargs)

    return wrapper


def format_pattern(pattern, replacement):
    log.info(f"Initializing pattern formatting with pattern: {pattern}")

    def decorator(func):
        log.debug("Setting up pattern formatting decorator")

        @wraps(func)
        def wrapper(data, *args, **kwargs):
            log.debug(
                f"Starting pattern formatting for data: {data[:100]}..."
            )  # Log first 100 chars
            data = re.sub(pattern=pattern, repl=replacement, string=data)
            log.debug("Pattern formatting completed")
            return func(data, *args, **kwargs)

        return wrapper

    return decorator


def standardize_name_fields(func):
    log.debug("Setting up name field standardization decorator")

    def _get_standardized_field(field_name, order):
        voter_name_pattern = VOTER_NAME_FIELD_DETECT_PATTERN
        makan_pattern = MAKAN_NUMBER_FIELD_DETECT_PATTERN
        voter_name_match = re.match(voter_name_pattern, field_name)
        makan_match = re.match(makan_pattern, field_name)
        if voter_name_match:
            first_word = voter_name_match.group(1).strip()
            if order == 1:
                return 'निर्वाचक का नाम'
            elif order == 2:
                return {
                    'पिता': 'पिता का नाम',
                    'पति': 'पति का नाम',
                    'माता': 'माता का नाम',
                    'पत्नी': 'पत्नी का नाम',
                }.get(first_word, 'पिता/पति का नाम')
        elif makan_match:
            return 'मकान संख्या'
        return field_name

    def _format_field(data, index, order):
        try:
            # Get items as a list of tuples (key, value)
            items = list(data.items())

            # Ensure the index is within bounds
            if index >= len(items):
                raise IndexError(
                    f"Index {index} out of range for dictionary with {len(items)} items."
                )

            # Extract key, value at the given index
            key, value = items[index]

            # Get the standardized key
            standardized_key = _get_standardized_field(key, order)

            # If the key doesn't need to be updated, return the original data
            if key == standardized_key:
                return data

            # Reconstruct the dictionary with the updated key at the correct position
            data = {
                k if i != index else standardized_key: v
                for i, (k, v) in enumerate(items)
            }

            return data
        except IndexError as e:
            log.error(f"Dictionary has fewer items than expected: {str(e)}")
            return data
        except Exception as e:
            log.error(f"Error standardizing field names: {str(e)}")
            return data

    @wraps(func)
    def wrapper(*args, **kwargs):
        data = func(*args, **kwargs)

        if not isinstance(data, dict) or not data:
            return data

        for i in range(3):
            data = _format_field(data=data, index=i, order=i + 1)
        return data

    return wrapper


def format_gender_age(func):
    log.debug("Setting up gender and age formatting")

    def _gender_age_replacement(match):
        if match.group(1):  # First pattern matched
            return f"उम्र:{match.group(2)}\nलिंग:{match.group(4)}"
        elif match.group(5):  # Second pattern matched
            return f"उम्र:{match.group(6)}\nलिंग:{match.group(8)}"
        return match.group(0)

    @wraps(func)
    def wrapper(data, *args, **kwargs):
        log.debug(
            f"Starting gender and age formatting for data: {data[:100]}..."
        )  # Log first 100 chars
        data = re.sub(GENDER_AGE_PATTERN, _gender_age_replacement, data)
        log.debug("Pattern formatting completed")
        return func(data, *args, **kwargs)

    return wrapper
