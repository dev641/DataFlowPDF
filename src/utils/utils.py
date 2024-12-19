import os
from pathlib import Path
from src.enums.enums import FileNamePart
from src.utils.logger import setup_logger

log = setup_logger(__name__)


def get_filename_part(pathname: str, part: FileNamePart = FileNamePart.FULL):
    """
    - Extracts specific parts of the filename based on the `part` argument.
    Returns:
    - str or None: The requested part of the filename, or None if an error occurs.
    """
    log.info(f"Extracting filename part: {part} from {pathname}")
    try:
        # Extract the file name from the full path
        file_name = os.path.basename(pathname)
        log.debug(f"Extracted base filename: {file_name}")

        if not file_name:
            log.error("Invalid pathname provided. Could not extract filename.")
            raise ValueError(
                "Invalid pathname provided. Could not extract filename."
            )

        # Determine the output based on the part
        if part == FileNamePart.FULL:
            log.debug(f"Returning full filename: {file_name}")
            return file_name  # Filename with extension
        elif part == FileNamePart.WITHOUT_EXTENSION:
            result = os.path.splitext(file_name)[0]
            log.debug(f"Returning filename without extension: {result}")
            return result
        elif part == FileNamePart.EXTENSION_ONLY:
            result = os.path.splitext(file_name)[1].lstrip(".")
            log.debug(f"Returning extension only: {result}")
            return result
        else:
            log.error(f"Invalid part specified: {part}")
            raise ValueError(
                "Invalid part specified. Choose FileNamePart.FULL, FileNamePart.WITHOUT_EXTENSION, or FileNamePart.EXTENSION_ONLY."
            )

    except ValueError as e:
        log.error(f"Value error: {e}")
        return None
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        return None


def make_dir(path: Path):
    """
    Creates a directory if it doesn't already exist.
    """
    log.info(f"Creating directory: {path}")
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            log.info(f"Directory created: {path}")
        else:
            log.info(f"Directory already exists: {path}")
    except Exception as e:
        log.error(f"Error creating directory: {e}")
