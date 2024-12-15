import sys
import os

# Add the project root to sys.path
current_dir = os.path.dirname(
    os.path.abspath(__file__)
)  # Directory of main.py
project_root = os.path.abspath(os.path.join(current_dir, ".."))  # One level up
sys.path.append(project_root)

# Now you can import config
from config.settings import CONFIG_FILES_DIR, PDF_DIR, PDF_PATH

from config.config_loader import load_enums

from src.processors.pdf.pdf_processor import PdfProcessor
from src.utils.logger import setup_logger

# Initialize logger
log = setup_logger(__name__)


def start():
    log.info("Starting PDF processing application")

    # Load the configuration
    log.debug("Loading configuration from %s", CONFIG_FILES_DIR)
    config = load_enums(config_dir=CONFIG_FILES_DIR)
    log.info("Configuration loaded successfully")

    # Process PDF files
    log.info("Scanning directory %s for PDF files", PDF_DIR)
    # for pdf_path in PDF_DIR.glob('*.pdf'):
    #     log.info("Processing PDF file: %s", pdf_path)
    #     pdf_processor = PdfProcessor(pdf_path=pdf_path)
    #     log.debug("PDF processor initialized for %s", pdf_path)

    pdf_processor = PdfProcessor(pdf_path=PDF_PATH)
    log.debug("PDF processor initialized for %s", PDF_PATH)
    pdf_processor.save_voter_information_from_pdf()


if __name__ == "__main__":
    start()
