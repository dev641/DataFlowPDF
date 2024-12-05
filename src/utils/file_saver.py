import json
import xml.etree.ElementTree as ET
import pandas as pd


class FileSaver:

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
