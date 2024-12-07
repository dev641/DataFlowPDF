import re
from src.enums.enums import CaseType


class CaseConverter:
    @staticmethod
    def normalize_string(input_string: str) -> str:
        """
        Normalizes the input string by converting it to a uniform format (snake_case)
        while preserving case information, to handle different input formats like
        camelCase, PascalCase, kebab-case, or snake_case.
        """
        # Replace hyphens or spaces with underscores, and split by different cases.
        # This ensures that camelCase, PascalCase, and kebab-case are normalized.
        normalized_string = re.sub(
            r"([a-z])([A-Z])", r"\1_\2", input_string
        )  # camelCase/PascalCase -> snake_case
        normalized_string = re.sub(
            r"[^a-zA-Z0-9]+", "_", normalized_string
        ).lower()
        return normalized_string

    @staticmethod
    def to_snake_case(input_string: str) -> str:
        """
        Converts a string to snake_case.
        """
        # Normalize the string to snake_case
        return CaseConverter.normalize_string(input_string)

    @staticmethod
    def to_camel_case(input_string: str) -> str:
        """
        Converts a string to camelCase.
        """
        normalized_string = CaseConverter.normalize_string(input_string)
        parts = normalized_string.split("_")
        return parts[0] + "".join(word.capitalize() for word in parts[1:])

    @staticmethod
    def to_pascal_case(input_string: str) -> str:
        """
        Converts a string to PascalCase.
        """
        normalized_string = CaseConverter.normalize_string(input_string)
        parts = normalized_string.split("_")
        return "".join(word.capitalize() for word in parts)

    @staticmethod
    def to_kebab_case(input_string: str) -> str:
        """
        Converts a string to kebab-case.
        """
        # Normalize string to snake_case and replace underscores with hyphens
        return CaseConverter.normalize_string(input_string).replace("_", "-")

    @staticmethod
    def to_upper_snake_case(input_string: str) -> str:
        """
        Converts a string to kebab-case.
        """
        # Normalize string to snake_case and replace underscores with hyphens
        return CaseConverter.normalize_string(input_string).upper()

    @staticmethod
    def convert(input_string: str, target_case: str) -> str:
        """
        Converts the input string to the desired case format.
        """
        if target_case == CaseType.SNAKE_CASE:
            return CaseConverter.to_snake_case(input_string)
        elif target_case == CaseType.CAMEL_CASE:
            return CaseConverter.to_camel_case(input_string)
        elif target_case == CaseType.PASCAL_CASE:
            return CaseConverter.to_pascal_case(input_string)
        elif target_case == CaseType.KEBAB_CASE:
            return CaseConverter.to_kebab_case(input_string)
        elif target_case == CaseType.UPPERCASE_SNAKE_CASE:
            return CaseConverter.to_upper_snake_case(input_string)
        else:
            raise ValueError("Unsupported target case")
