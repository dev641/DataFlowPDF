from enum import Enum


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
