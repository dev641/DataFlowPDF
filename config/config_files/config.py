from enum import Enum


class ImageProcess(Enum):
    class Thresholds(Enum):
        class VoterBox(Enum):
            POSITION_THRESHOLD = 500
            SIZE_THRESHOLD = 200

            class Area(Enum):
                MIN = 2000000
                MAX = 3000000

            class AspectRatio(Enum):
                MIN = 2.4
                MAX = 2.6

        class PassportBox(Enum):
            class AreaThresholdRange(Enum):
                MIN = 0.05
                MAX = 0.15

            class AspectRatioRange(Enum):
                MIN = 0.7
                MAX = 1.5


class OcrProcess(Enum):
    OCR_ENGINE = ["PYTESSERACT", "EASYOCR"]

    class Pytesseract(Enum):
        class Config(Enum):
            DEFAULT = ""
            ONE = "--psm 6 --oem 3"
            TWO = "--psm 6 --oem 3"
            THREE = "--psm 6 --oem 3"
            FOUR = "--psm 6 --oem 3"

        class Lang(Enum):
            ENGLISH = "eng"
            HINDI = "hin"
            HIN_ENG = "hin+eng"
            ENGLISH_HINDI = "eng+hin"

    class Easyocr(Enum):
        class Lang(Enum):
            ENGLISH = "en"
            HINDI = "hi"
            HIN_ENG = "hi+en"
            ENGLISH_HINDI = "en+hi"
