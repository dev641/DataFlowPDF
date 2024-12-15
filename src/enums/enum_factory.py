from enum import Enum
from pathlib import Path
import yaml
from src.utils.utils import get_filename_part
from src.processors.text.case_converter import CaseConverter
from src.enums.enums import FileNamePart, CaseType, FieldType
from collections.abc import Iterable
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class EnumFactory:
    """
    A factory class to dynamically create nested enums from dictionaries.
    """

    @staticmethod
    def create_enum(name: str, data):
        """
        Recursively create an Enum or a nested structure of Enums from a dictionary.
        """
        log.info(f"Creating enum: {name}")
        log.debug(f"Input data type: {type(data)}")

        if isinstance(data, dict):
            log.debug(f"Processing dictionary with {len(data)} items")
            # Create a nested structure of Enums for dictionaries
            attributes = {
                key.upper(): (
                    EnumFactory.create_enum(
                        f"{name}_{key.capitalize()}", value
                    )
                    if isinstance(value, dict)
                    else value
                )
                for key, value in data.items()
            }
            log.debug(f"Created attributes: {list(attributes.keys())}")

            enum_type = type(name, (Enum,), attributes)
            log.info(f"Successfully created enum: {name}")
            return enum_type

        log.warning(f"Unsupported data type for enum creation: {type(data)}")
        return None

    @staticmethod
    def generate_enum_code(config_dir: Path, output_file: Path):
        """
        Generates Python Enums from all YAML files in the specified directory.
        """
        log.info(f"Starting enum code generation from directory: {config_dir}")

        lines = [
            "from enum import Enum",
            "import cv2 as cv\n\n",
        ]
        log.debug("Initialized base imports")

        # Generate an enum for each YAML file
        for yaml_file in config_dir.glob("*.yml"):
            log.debug(f"Processing YAML file: {yaml_file}")

            with open(yaml_file, "r") as file:
                config = yaml.safe_load(file)
                log.debug(f"Loaded configuration from {yaml_file}")

            class_name = get_filename_part(
                pathname=yaml_file, part=FileNamePart.WITHOUT_EXTENSION
            )
            log.debug(f"Generated class name: {class_name}")

            class_name = CaseConverter.convert(
                input_string=class_name, target_case=CaseType.PASCAL_CASE
            )
            log.debug(f"Converted class name to PascalCase: {class_name}")

            EnumFactory._handle_nested_dict(
                class_name=class_name, config=config, lines=lines
            )
            log.debug(f"Processed nested dictionary for {class_name}")

        log.info(f"Writing generated enum code to: {output_file}")
        with open(output_file, "w") as file:
            file.write("\n".join(lines))

        log.info("Enum code generation completed successfully")

    @staticmethod
    def _format_enum_value(value):
        log.info("Starting enum value formatting")
        log.debug(f"Input value type: {type(value)}")

        if (
            isinstance(value, dict)
            and 'type' in value
            and value['type'] == FieldType.VARIABLE.value
        ):
            log.debug("Processing variable type field")
            enum_value = value["value"]
            log.debug(f"Extracted value: {enum_value}")
        else:
            log.debug("Processing standard field")
            if isinstance(value, Iterable) and 'value' in value:
                enum_value = repr(value['value'])
            else:
                enum_value = repr(value)
            log.debug(f"Formatted value: {enum_value}")

        log.info("Enum value formatting completed")
        return enum_value

    @staticmethod
    def _handle_nested_dict(class_name, config, lines, indent=0):
        """
        Handles nested dictionaries and generates enum-like structures.
        """
        log.info(f"Processing nested dictionary for class: {class_name}")

        if config is not None:
            indent_space = "    " * indent
            log.debug(f"Using indent level: {indent}")

            lines.append(f"{indent_space}class {class_name}:")
            log.debug(f"Added class declaration: {class_name}")

            for key, value in config.items():
                if isinstance(value, dict) and 'type' not in value:
                    log.debug(f"Found nested dictionary for key: {key}")
                    class_name = CaseConverter.convert(
                        input_string=key, target_case=CaseType.PASCAL_CASE
                    )
                    EnumFactory._handle_nested_dict(
                        class_name=class_name,
                        config=value,
                        lines=lines,
                        indent=indent + 1,
                    )
                else:
                    key = CaseConverter.convert(
                        input_string=key,
                        target_case=CaseType.UPPERCASE_SNAKE_CASE,
                    )
                    log.debug(f"Processing enum value for key: {key}")
                    lines.append(
                        f"{indent_space}    {key} = {EnumFactory._format_enum_value(value)}"
                    )

        log.info(f"Completed nested dictionary processing for: {class_name}")
