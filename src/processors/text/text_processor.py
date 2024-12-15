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
    GenderAgePAttern,
)
import re


class TextProcessor:
    def __init__(self):
        # self.text = text
        pass

    @staticmethod
    def _extract_user_data(self, roi_data):
        user_data = []
        for data_list in roi_data:
            if ':' in data_list:
                if data_list.count(':') > 1:
                    data = data_list.split(" ")
                    data = [i.strip().split(':') for i in data]
                    user_data.extend(data)
                else:
                    data = data_list.split(":")
                    data = [i.strip() for i in data]
                    user_data.append(data)
            else:
                data_list = re.sub(r"\s+", "", data_list)
                if re.match(VOTER_ID_PATTERN, data_list):
                    user_data.append(['id', data_list])
        return user_data

    @staticmethod
    def _convert_digits_in_user_data(self, user_data):
        return [
            (
                [item[0], self.convert_hindi_to_english_digits(item[1])]
                if len(item) > 1
                else item
            )
            for item in user_data
        ]

    @staticmethod
    def _create_user_dict(self, user_data):
        return {
            item[0] if len(item) > 0 and item[0] else None: (
                item[1] if len(item) > 1 and item[1] else None
            )
            for item in user_data
        }

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
            user_data = self._extract_user_data(roi_data)
            # Convert Hindi numerals to English
            user_data = self._convert_digits_in_user_data(user_data)

            return self._create_user_dict(user_data)

        except Exception as e:
            print(f"An error occurred during text formatting: {e}")
            return {}
