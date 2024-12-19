import yaml
import json
from pathlib import Path
from src.enums.enum_factory import EnumFactory
from src.decorator.class_decorator import singleton
from config.settings import (
    CONFIG_FILES_DIR,
    CONFIG_FILE_PATH,
)
from src.enums.enums import FileNamePart
from src.utils.utils import get_filename_part

from config.config_files.config import ImageProcess


@singleton
class ConfigLoader:
    def __init__(
        self,
        config_dir: Path = CONFIG_FILES_DIR,
        output_file: Path = CONFIG_FILE_PATH,
    ):
        self.config_dir = config_dir
        self.output_file = output_file

    def update_enum(self):
        EnumFactory.generate_enum_code(
            config_dir=self.config_dir, output_file=self.output_file
        )

    def load_json(self, file_path: Path):
        with open(file_path, "r", encoding='utf-8') as file:
            data = json.load(file)
        return data


def _config_loader():
    return ConfigLoader(
        config_dir=CONFIG_FILES_DIR,
        output_file=CONFIG_FILE_PATH,
    )


def load_enums(config_dir=CONFIG_FILES_DIR):
    # Instantiate ConfigLoader with paths
    # Generate Enums
    _config_loader().update_enum()


def load_json(filePath: Path):
    # Load OCR corrections from file
    return _config_loader().load_json(filePath)


def test_enum():
    print(ImageProcess.Counters.ImageRoi.MODE)
