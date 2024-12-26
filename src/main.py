import sys
import os
import time
import multiprocessing

# Add the project root to sys.path
current_dir = os.path.dirname(
    os.path.abspath(__file__)
)  # Directory of main.py
project_root = os.path.abspath(os.path.join(current_dir, ".."))  # One level up
sys.path.append(project_root)

# Now you can import config
from config.settings import (
    CONFIG_FILES_DIR,
    PDF_DIR,
    PDF_PATH,
    PDF_PROCESS_CONTROL,
)

from config.config_loader import load_enums

from src.processors.pdf.pdf_processor import PdfProcessor
from src.utils.logger import setup_logger
from src.decorator.system_service import start_service
from src.enums.enums import ServiceName

# Initialize logger
log = setup_logger(__name__)


def process_pdf(pdf_path):
    # Create a PdfProcessor instance
    pdf_processor = PdfProcessor(pdf_path=pdf_path)
    log.debug(f"PDF processor initialized for {pdf_path}")
    pdf_processor.save_voter_information_from_pdf()
    log.info(f"PDF processing completed for {pdf_path}")


@start_service(service_name=ServiceName.DATABASE.value)
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
    pdf_paths = list(PDF_DIR.glob("*.pdf"))
    log.info("Found %s PDF files in %s", len(pdf_paths), PDF_DIR)

    num_processes = min(
        PDF_PROCESS_CONTROL, multiprocessing.cpu_count(), len(pdf_paths)
    )

    log.info("Starting PDF processing with %s processes", num_processes)
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.map(process_pdf, pdf_paths)


if __name__ == "__main__":
    start_time = time.time()
    start()

    end_time = time.time()
    execution_time = end_time - start_time

    minutes = int(execution_time // 60)
    seconds = int(execution_time % 60)
    log.info(f"Total execution time: {minutes} minutes {seconds} seconds")
