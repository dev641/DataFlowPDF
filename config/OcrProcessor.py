from enum import Enum

class OCR_ENGINE(Enum):
    """Enum for configuration options"""
    PYTESSERACT = "pytesseract"
    EASYOCR = "easyocr"


# OCR Configuration
class PYTESSERACT(Enum):
    """Configuration for PyTesseract OCR"""
    class CONFIG(Enum):
        """Configuration for OCR"""
        DEFAULT = ""
        ONE = "--psm 6 --oem 3"
        TWO = "--psm 6 --oem 3"
        THREE = "--psm 6 --oem 3"
        FOUR = "--psm 6 --oem 3"
    class LANG(Enum):
        """Language for OCR"""
        ENGLISH = "eng"
        HINDI = "hin"
        HIN_ENG = "hin+eng"
        ENGLISH_HINDI = "eng+hin"

class EASYOCR(Enum):
    """Configuration for EasyOCR"""
    class LANG(Enum):
        """Language for OCR"""
        ENGLISH = "en"
        HINDI = "hi"
        HIN_ENG = "hi+en"
        ENGLISH_HINDI = "en+hi"
            
