from enum import Enum


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
