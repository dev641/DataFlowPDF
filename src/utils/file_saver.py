import json
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import uuid
from pathlib import Path
from config.settings import PDF_OUTPUT_PATH
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class FileSaver:

    @staticmethod
    def save_data(data, file_name: str, output_path: Path = PDF_OUTPUT_PATH):
        log.info(f"Starting data save process for: {file_name}")
        filename = FileSaver.generate_unique_filename(filename=file_name)
        log.debug(f"Generated unique filename: {filename}")

        file_path = output_path / filename
        log.debug(f"Saving data to path: {file_path}")

        FileSaver.save_to_json(data=data, file_path=f"{file_path}.json")
        log.info("Data successfully saved to JSON file")

        FileSaver.save_to_excel(data=data, file_path=f"{file_path}.xlsx")
        log.info("Data successfully saved to Excel file")

    @staticmethod
    def generate_unique_filename(filename: str, prefix: str = "") -> str:
        log.info(f"Generating unique filename for: {filename}")

        # Get timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log.debug(f"Generated timestamp: {timestamp}")

        # Get unique ID
        unique_id = str(uuid.uuid4())[:8]
        log.debug(f"Generated unique ID: {unique_id}")

        # Combine components
        unique_filename = f"{prefix}_{filename}_{timestamp}_{unique_id}"
        log.info(f"Created unique filename: {unique_filename}")

        return unique_filename

    @staticmethod
    def save_to_json(data: dict, file_path: str):
        log.info(f"Starting JSON save to: {file_path}")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            log.info("Successfully saved data to JSON file")

        except IOError as e:
            log.error(f"IO Error while saving JSON file: {e}")
            raise

        except TypeError as e:
            log.error(f"Type Error in JSON serialization: {e}")
            raise

        except Exception as e:
            log.error(f"Unexpected error during JSON save: {e}")
            raise

    @staticmethod
    def save_to_excel(data: dict, file_path: str):
        log.info(f"Starting Excel save to: {file_path}")
        try:
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False)
            log.info("Successfully saved data to Excel file")

        except ValueError as e:
            log.error(f"Value Error during DataFrame creation: {e}")
            raise

        except IOError as e:
            log.error(f"IO Error while saving Excel file: {e}")
            raise

        except Exception as e:
            log.error(f"Unexpected error during Excel save: {e}")
            raise

    @staticmethod
    def save_to_xml(data: dict, file_path: str):
        log.info(f"Starting XML save to: {file_path}")
        try:
            root = ET.Element("root")
            log.debug("Created XML root element")

            for key, value in data.items():
                child = ET.SubElement(root, key)
                child.text = str(value)
            log.debug(f"Added {len(data)} elements to XML tree")

            tree = ET.ElementTree(root)
            tree.write(file_path)
            log.info("Successfully saved data to XML file")

        except TypeError as e:
            log.error(f"Type Error during XML creation: {e}")
            raise

        except IOError as e:
            log.error(f"IO Error while saving XML file: {e}")
            raise

        except Exception as e:
            log.error(f"Unexpected error during XML save: {e}")
            raise

    @staticmethod
    def save_to_text(data: str, file_path: str):
        log.info(f"Starting text save to: {file_path}")
        try:
            with open(file_path, 'w') as text_file:
                text_file.write(data)
            log.info("Successfully saved data to text file")

        except IOError as e:
            log.error(f"IO Error while saving text file: {e}")
            raise

        except Exception as e:
            log.error(f"Unexpected error during text save: {e}")
            raise
