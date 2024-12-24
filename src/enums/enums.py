from enum import Enum
from config.settings import (
    # GENDER_AGE_PATTERN,
    # GENDER_AGE_PATTERN_REPLACEMENT,
    IMAGE_EXTENSIONS,
)


class OcrEngine(Enum):
    TENSORFLOW = "tensorflow"
    PYTESSERACT = "pytesseract"
    EASYOCR = "easyocr"


# Define an Enum class
class FileNamePart(Enum):
    FULL = "full"  # Represents the full filename with extension
    WITHOUT_EXTENSION = "name"  # Represents the filename without extension
    EXTENSION_ONLY = "ext"  # Represents only the extension


class CaseType(Enum):
    SNAKE_CASE = "snake_case"
    CAMEL_CASE = "camelCase"
    PASCAL_CASE = "PascalCase"
    KEBAB_CASE = "kebab-case"
    UPPERCASE_SNAKE_CASE = "UPPERCASE_SNAKE_CASE"


class FieldType(Enum):
    CONSTANT = "constant"
    VARIABLE = "variable"


class ImageType(Enum):
    ROI_IMAGE = "roi_image"
    MASK_IMAGE = "mask_image"
    ORIGINAL_IMAGE = "original_image"
    PASSPORT = "passport"


# class GenderAgePAttern(Enum):
#     PATTERN = GENDER_AGE_PATTERN
#     REPLACEMENT = GENDER_AGE_PATTERN_REPLACEMENT


class ImageExtensions(Enum):
    PNG = ".png"
    JPG = ".jpg"
    JPEG = ".jpeg"

    @classmethod
    def _generate_enum_values(cls):
        return {ext.upper().lstrip('.'): ext for ext in IMAGE_EXTENSIONS}

    def __new__(cls, value):
        # Ensure the value is correctly passed to the base `Enum` class
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def get_extension(self, with_period: bool = True) -> str:
        return self.value if with_period else self.value.lstrip('.')


class ServiceName(Enum):
    DATABASE = "MSSQL$SQLEXPRESS"
