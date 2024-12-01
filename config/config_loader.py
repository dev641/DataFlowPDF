import yaml
from pathlib import Path
from src.enums.enum_factory import EnumFactory
from settings import CONFIG_FILES_DIR, CONFIG_FILE_PATH
from src.enums.enums import FileNamePart
from src.utils.utils import get_filename_part


class ConfigLoader:
    def __init__(
        self,
        yaml_dir: Path = CONFIG_FILES_DIR,
        output_file: Path = CONFIG_FILE_PATH,
    ):
        self.yaml_dir = yaml_dir
        self.output_file = output_file

    def update_enum(self):
        EnumFactory.generate_enum_code(
            yaml_dir=self.yaml_dir, output_file=self.output_file
        )


def load_enums(yaml_dir=CONFIG_FILES_DIR):
    # Instantiate ConfigLoader with paths
    loader = ConfigLoader(
        yaml_dir=CONFIG_FILES_DIR, output_file=CONFIG_FILE_PATH
    )
    # Generate Enums
    loader.update_enum()
