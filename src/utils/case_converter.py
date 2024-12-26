import re
from src.enums.enums import CaseType
from src.utils.logger import setup_logger

# Initialize logger
log = setup_logger(__name__)


class CaseConverter:
    @staticmethod
    def normalize_string(input_string: str) -> str:
        """
        Normalizes the input string by converting it to a uniform format (snake_case)
        while preserving case information, to handle different input formats like
        camelCase, PascalCase, kebab-case, or snake_case.
        """
        log.info("Starting string normalization")
        log.debug(f"Input string: {input_string}")

        # Replace hyphens or spaces with underscores, and split by different cases.
        # This ensures that camelCase, PascalCase, and kebab-case are normalized.
        log.debug("Converting camelCase/PascalCase to snake_case")
        normalized_string = re.sub(r"([a-z])([A-Z])", r"\1_\2", input_string)

        log.debug("Converting special characters to underscores")
        normalized_string = re.sub(
            r"[^a-zA-Z0-9]+", "_", normalized_string
        ).lower()

        log.info("String normalization completed")
        return normalized_string

    @staticmethod
    def to_snake_case(input_string: str) -> str:
        """
        Converts a string to snake_case.
        """
        log.info("Converting string to snake_case")
        log.debug(f"Input string: {input_string}")

        # Normalize the string to snake_case
        normalized = CaseConverter.normalize_string(input_string)

        log.info("Successfully converted to snake_case")
        return normalized

    @staticmethod
    def to_camel_case(input_string: str) -> str:
        """
        Converts a string to camelCase.
        """
        log.info("Converting string to camelCase")
        log.debug(f"Input string: {input_string}")

        normalized_string = CaseConverter.normalize_string(input_string)
        parts = normalized_string.split("_")

        log.debug(f"Split parts: {parts}")
        camel_case = parts[0] + ''.join(part.title() for part in parts[1:])

        log.info("Successfully converted to camelCase")
        return camel_case

    @staticmethod
    def to_pascal_case(input_string: str) -> str:
        """
        Converts a string to PascalCase.
        """
        log.info("Converting string to PascalCase")
        log.debug(f"Input string: {input_string}")

        normalized_string = CaseConverter.normalize_string(input_string)
        parts = normalized_string.split("_")

        log.debug(f"Split parts: {parts}")
        pascal_case = ''.join(part.title() for part in parts)

        log.info("Successfully converted to PascalCase")
        return pascal_case

    @staticmethod
    def to_kebab_case(input_string: str) -> str:
        """
        Converts a string to kebab-case.
        """
        log.info("Converting string to kebab-case")
        log.debug(f"Input string: {input_string}")

        # Normalize string to snake_case and replace underscores with hyphens
        kebab_case = CaseConverter.normalize_string(input_string).replace(
            "_", "-"
        )

        log.info("Successfully converted to kebab-case")
        return kebab_case

    @staticmethod
    def to_upper_snake_case(input_string: str) -> str:
        """
        Converts a string to UPPER_SNAKE_CASE.
        """
        log.info("Converting string to UPPER_SNAKE_CASE")
        log.debug(f"Input string: {input_string}")

        upper_snake = CaseConverter.normalize_string(input_string).upper()

        log.info("Successfully converted to UPPER_SNAKE_CASE")
        return upper_snake

    @staticmethod
    def convert(input_string: str, target_case: str) -> str:
        """
        Converts the input string to the desired case format.
        """
        log.info(f"Converting string to {target_case}")
        log.debug(f"Input string: {input_string}")

        if target_case == CaseType.SNAKE_CASE:
            log.debug("Using snake_case conversion")
            return CaseConverter.to_snake_case(input_string)
        elif target_case == CaseType.CAMEL_CASE:
            log.debug("Using camelCase conversion")
            return CaseConverter.to_camel_case(input_string)
        elif target_case == CaseType.PASCAL_CASE:
            log.debug("Using PascalCase conversion")
            return CaseConverter.to_pascal_case(input_string)
        elif target_case == CaseType.KEBAB_CASE:
            log.debug("Using kebab-case conversion")
            return CaseConverter.to_kebab_case(input_string)
        elif target_case == CaseType.UPPERCASE_SNAKE_CASE:
            log.debug("Using UPPER_SNAKE_CASE conversion")
            return CaseConverter.to_upper_snake_case(input_string)

        log.warning(f"Unsupported case type: {target_case}")
        return input_string
