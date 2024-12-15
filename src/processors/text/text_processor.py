from config.config_loader import load_json
from src.decorator.decorator import (
    correct_misspelled_word,
    hindi_to_english_digits,
    format_pattern,
    normalize_text,
    clean_empty_lines,
)
from config.settings import (
    VOTER_ID_PATTERN,
    OCR_CORRECTIONS_PATH,
    HIN_ENG_DIGITS_PATH,
)
from src.enums.enums import GenderAgePAttern
import re
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class TextProcessor:
    def __init__(self):
        # self.text = text
        pass

    @staticmethod
    def _extract_user_data(self, roi_data):
        log.info("Starting user data extraction")
        user_data = []

        log.debug(f"Processing {len(roi_data)} data items")
        for data_list in roi_data:
            if ':' in data_list:
                if data_list.count(':') > 1:
                    log.debug(f"Multiple colons found in: {data_list}")
                    data = data_list.split(" ")
                    data = [i.strip().split(':') for i in data]
                    user_data.extend(data)
                else:
                    log.debug(f"Single colon found in: {data_list}")
                    data = data_list.split(":")
                    data = [i.strip() for i in data]
                    user_data.append(data)
            else:
                data_list = re.sub(r"\s+", "", data_list)
                if re.match(VOTER_ID_PATTERN, data_list):
                    log.debug(f"Voter ID found: {data_list}")
                    user_data.append(['id', data_list])

        log.info(f"Extracted {len(user_data)} user data items")
        return user_data

    @staticmethod
    @hindi_to_english_digits(filePath=HIN_ENG_DIGITS_PATH)
    def _convert_digits_in_user_data(self, user_data):
        log.info("Starting digit conversion in user data")
        log.debug(f"Processing {len(user_data)} data items")

        converted_data = [
            (
                [item[0], self.convert_hindi_to_english_digits(item[1])]
                if len(item) > 1
                else item
            )
            for item in user_data
        ]

        log.info(f"Completed digit conversion for {len(converted_data)} items")
        return converted_data

    @staticmethod
    def create_user_dict(self, user_data):
        log.info("Starting user dictionary creation")
        log.debug(f"Processing {len(user_data)} user data items")

        user_dict = {
            item[0] if len(item) > 0 and item[0] else None: (
                item[1] if len(item) > 1 and item[1] else None
            )
            for item in user_data
        }

        log.info(f"Created user dictionary with {len(user_dict)} entries")
        return user_dict

    @staticmethod
    @clean_empty_lines
    @normalize_text
    @format_pattern(
        pattern=GenderAgePAttern.PATTERN,
        replacement=GenderAgePAttern.REPLACEMENT,
    )
    @correct_misspelled_word(filePath=OCR_CORRECTIONS_PATH)
    def format_text(self, roi_data):
        try:
            log.info("Starting text formatting")
            log.debug(
                f"Processing ROI data: {roi_data[:100]}..."
            )  # First 100 chars

            user_data = self._extract_user_data(roi_data)
            log.debug(f"Extracted {len(user_data)} user data items")

            # Convert Hindi numerals to English
            user_data = self._convert_digits_in_user_data(user_data)
            log.debug("Completed Hindi to English digit conversion")

            result = self._create_user_dict(user_data)
            log.info(f"Text formatting completed with {len(result)} entries")
            return result

        except Exception as e:
            log.error(f"Error during text formatting: {e}")
            return {}
