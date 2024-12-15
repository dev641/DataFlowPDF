import json
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import uuid
from pathlib import Path
from config.settings import PDF_OUTPUT_PATH


class FileSaver:

    @staticmethod
    def save_data(data, file_name: str, output_path: Path = PDF_OUTPUT_PATH):
        filename = FileSaver.generate_unique_filename(filename=file_name)
        file_path = output_path / filename
        FileSaver.save_to_json(data=data, file_path=f"{file_path}.json")
        FileSaver.save_to_excel(data=data, file_path=f"{file_path}.xlsx")

    @staticmethod
    def generate_unique_filename(filename: str, prefix: str = "") -> str:
        # Get timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get unique ID
        unique_id = str(uuid.uuid4())[:8]

        # Combine components
        filename = f"{prefix}_{filename}_{timestamp}_{unique_id}"

        return filename

    @staticmethod
    def save_to_json(data: dict, file_path: str):
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def save_to_excel(data: dict, file_path: str):
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False, engine='openpyxl')

    @staticmethod
    def save_to_xml(data: dict, file_path: str):
        root = ET.Element("root")
        for key, value in data.items():
            child = ET.SubElement(root, key)
            child.text = str(value)
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def save_to_text(data: str, file_path: str):
        with open(file_path, 'w') as text_file:
            text_file.write(data)
