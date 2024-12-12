import yaml
import json
from pathlib import Path
from src.enums.enum_factory import EnumFactory
from src.decorator.class_decorator import singleton
from config.settings import (
    CONFIG_FILES_DIR,
    CONFIG_FILE_PATH,
    OCR_CORRECTIONS_PATH,
)
from src.enums.enums import FileNamePart
from src.utils.utils import get_filename_part

from config.config_files.config import ImageProcess


@singleton
class ConfigLoader:
    def __init__(
        self,
        yaml_dir: Path = CONFIG_FILES_DIR,
        ocr_corrections_path: Path = OCR_CORRECTIONS_PATH,
        output_file: Path = CONFIG_FILE_PATH,
    ):
        self.yaml_dir = yaml_dir
        self.output_file = output_file
        self.ocr_corrections_path = ocr_corrections_path

    def update_enum(self):
        EnumFactory.generate_enum_code(
            yaml_dir=self.yaml_dir, output_file=self.output_file
        )

    def load_json(self, file_path: Path):
        with open(file_path, "r") as file:
            data = json.load(file)
        return data


def _config_loader():
    return ConfigLoader(
        yaml_dir=CONFIG_FILES_DIR,
        output_file=CONFIG_FILE_PATH,
        ocr_corrections_path=OCR_CORRECTIONS_PATH,
    )


def load_enums(yaml_dir=CONFIG_FILES_DIR):
    # Instantiate ConfigLoader with paths
    # Generate Enums
    _config_loader().update_enum()


def load_ocr_corrections():
    # Load OCR corrections from file
    return _config_loader().load_json(OCR_CORRECTIONS_PATH)


def test_enum():
    print(ImageProcess.Counters.ImageRoi.MODE)
