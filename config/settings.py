from pathlib import Path
import sys
from enum import Enum

# All Project Directories
ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = Path(__file__).resolve().parent
CONFIG_FILES_DIR = CONFIG_DIR / "config_files"
OCR_CORRECTIONS_PATH = CONFIG_FILES_DIR / "ocr_corrections.json"
HIN_ENG_DIGITS_PATH = CONFIG_FILES_DIR / "hin_eng_digits.json"
CONFIG_FILE_PATH = CONFIG_FILES_DIR / "config.py"
DATA_DIR = ROOT_DIR / "data"
SRC_DIR = ROOT_DIR / "src"
TEMP_IMG_DIR = ROOT_DIR / ".temp/image"
ROI_PATH = TEMP_IMG_DIR / "roi"
PDF_DIR = DATA_DIR / "pdfs"
UTILS_DIR = SRC_DIR / "utils"
PDF_PATH = PDF_DIR / "2024-FC-EROLLGEN-S04-196-FinalRoll-Revision5-HIN-1.pdf"


# Pattern Settings
VOTER_ID_PATTERN = r"\b([A-Z]{2}/\d{2}/\d{3}/\d{6})|([A-Z]{3}\d{7})\b"


class GenderAgePAttern(Enum):
    PATTERN = r"(उम्र):?\s*(\d+)\s*(लिंग)"
    REPLACEMENT = r'\1:\2 \3'


IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"]
