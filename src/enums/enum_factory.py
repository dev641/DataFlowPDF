from enum import Enum
from pathlib import Path
import yaml
from src.utils.utils import get_filename_part
from src.processors.text.case_converter import CaseConverter
from src.enums.enums import FileNamePart, CaseType, FieldType
from collections.abc import Iterable


class EnumFactory:
    """
    A factory class to dynamically create nested enums from dictionaries.
    """

    @staticmethod
    def create_enum(name: str, data):
        """
        Recursively create an Enum or a nested structure of Enums from a dictionary.

        Args:
            name (str): Name of the Enum to be created.
            data (dict): Dictionary from which the Enum will be generated.

        Returns:
            type: A dynamically created Enum or nested structure of Enums.
        """
        if isinstance(data, dict):
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
            return type(name, (Enum,), attributes)
        else:
            raise ValueError("Top-level data must be a dictionary.")

    @staticmethod
    def generate_enum_code(config_dir: Path, output_file: Path):
        """
        Generates Python Enums from all YAML files in the specified directory.

        Args:
            yaml_dir (Path): Path to the directory containing YAML files.
            output_file (Path): Path to the output Python file.
        """
        lines = [
            "from enum import Enum",
            "import cv2 as cv\n\n",
        ]  # Initialize the generated file content

        # Generate an enum for each YAML file
        for yaml_file in config_dir.glob("*.yml"):
            with open(yaml_file, "r") as file:
                config = yaml.safe_load(file)
            class_name = get_filename_part(
                pathname=yaml_file, part=FileNamePart.WITHOUT_EXTENSION
            )  # Use file name as the base class name
            class_name = CaseConverter.convert(
                input_string=class_name, target_case=CaseType.PASCAL_CASE
            )
            # handle_nested_dict(class_name, config)/
            EnumFactory._handle_nested_dict(
                class_name=class_name, config=config, lines=lines
            )

        # Write the generated file
        with open(output_file, "w") as file:
            file.writelines("\n".join(lines))

    @staticmethod
    def _format_enum_value(value):
        """
        Formats the enum value based on its type.
        """
        if (
            isinstance(value, dict)
            and 'type' in value
            and value['type'] == FieldType.VARIABLE.value
        ):
            # Handle the case where 'type' is present in the dictionary
            enum_value = value["value"]
        else:
            # Handle the case where 'type' is not present or not a dictionary
            if isinstance(value, Iterable) and 'value' in value:
                enum_value = repr(value['value'])
            else:
                enum_value = repr(value)
        return enum_value

    @staticmethod
    def _handle_nested_dict(class_name, config, lines, indent=0):
        """
        Handles nested dictionaries and generates enum-like structures.
        """
        if config is not None:
            indent_space = "    " * indent
            lines.append(f"{indent_space}class {class_name}:")
            for key, value in config.items():
                if isinstance(value, dict) and 'type' not in value:
                    # Recursively handle nested dictionaries
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
                    # Add key-value pair to enum
                    lines.append(
                        f"{indent_space}    {key} = {EnumFactory._format_enum_value(value)}"
                    )

        # Add a blank line for separation
        lines.append("")
