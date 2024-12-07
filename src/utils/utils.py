import os
from src.enums.enums import FileNamePart


def get_filename_part(pathname: str, part: FileNamePart = FileNamePart.FULL):
    """
    - Extracts specific parts of the filename based on the `part` argument.
    Returns:
    - str or None: The requested part of the filename, or None if an error occurs.
    """
    try:
        # Extract the file name from the full path
        file_name = os.path.basename(pathname)
        if not file_name:
            raise ValueError(
                "Invalid pathname provided. Could not extract filename."
            )

        # Determine the output based on the part
        if part == FileNamePart.FULL:
            return file_name  # Filename with extension
        elif part == FileNamePart.WITHOUT_EXTENSION:
            return os.path.splitext(file_name)[0]  # Filename without extension
        elif part == FileNamePart.EXTENSION_ONLY:
            return os.path.splitext(file_name)[1].lstrip(".")  # Extension only
        else:
            raise ValueError(
                "Invalid part specified. Choose FileNamePart.FULL, FileNamePart.WITHOUT_EXTENSION, or FileNamePart.EXTENSION_ONLY."
            )

    except ValueError as e:
        print(f"Value error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
