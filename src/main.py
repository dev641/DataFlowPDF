import sys
import os

# Add the project root to sys.path
current_dir = os.path.dirname(
    os.path.abspath(__file__)
)  # Directory of main.py
project_root = os.path.abspath(os.path.join(current_dir, ".."))  # One level up
sys.path.append(project_root)

# Now you can import config
from config.settings import CONFIG_FILES_DIR, PDF_DIR

from config.config_loader import load_enums

from src.processors.pdf.pdf_processor import PdfProcessor


def start():
    # Load the configuration
    config = load_enums(config_dir=CONFIG_FILES_DIR)
    for pdf_path in PDF_DIR.glob('*.pdf'):
        pdf_processor = PdfProcessor(pdf_path=pdf_path)
        pdf_processor.save_voter_information_from_pdf()


if __name__ == "__main__":
    start()
