import fitz
from PIL import Image
from config.settings import IMAGE_DPI, IMAGE_MODE
import numpy as np
from src.utils.logger import setup_logger
from src.utils.utils import get_filename_part
from src.enums.enums import FileNamePart

log = setup_logger(__name__)


class PdfReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def process_pdf(self, process_func):
        log.info(f"Starting to read PDF file: {self.file_path}")
        try:
            log.debug("Opening PDF file with fitz")
            with fitz.open(self.file_path) as pdf:
                log.info(
                    f"Successfully opened PDF with {pdf.page_count} pages"
                )
                process_func(pdf)

        except fitz.FileDataError:
            log.error(f"Invalid or corrupted PDF file: {self.file_path}")
            return None
        except FileNotFoundError:
            log.error(f"PDF file not found: {self.file_path}")
            return None
        except Exception as e:
            log.error(f"Error reading PDF file {self.file_path}: {str(e)}")
            return None

    def _get_page_from_pdf(self, pdf, page_num):
        log.info(f"Getting page {page_num} from PDF")
        try:
            log.debug(f"Accessing page {page_num}")
            page = pdf[page_num]
            log.info(f"Successfully retrieved page {page_num}")
            return page

        except IndexError:
            log.error(f"Page number {page_num} is out of range")
            return None
        except ValueError:
            log.error(f"Invalid page number {page_num}")
            return None
        except Exception as e:
            log.error(f"Error accessing page {page_num}: {str(e)}")
            return None

    def extract_image_from_pdf(self, pdf, page_num):
        log.info(f"Starting image extraction from page {page_num}")
        try:
            log.debug(f"Getting page {page_num} from PDF")
            page = self._get_page_from_pdf(pdf=pdf, page_num=page_num)

            if page is None:
                log.error(f"Failed to get page {page_num}")
                return None

            log.debug(f"Creating pixmap with DPI={IMAGE_DPI}")
            pix = page.get_pixmap(dpi=IMAGE_DPI)

            log.debug(f"Converting pixmap to image with mode {IMAGE_MODE}")
            img = Image.frombytes(
                IMAGE_MODE, [pix.width, pix.height], pix.samples
            )

            log.debug("Converting image to numpy array")
            img_np = np.array(img)

            log.info("Successfully extracted image from PDF")
            return img_np

        except AttributeError:
            log.error("Invalid page object or missing pixmap method")
            return None
        except ValueError:
            log.error("Invalid image data or conversion failed")
            return None
        except Exception as e:
            log.error(
                f"Error extracting image from PDF page {page_num}: {str(e)}"
            )
            return None

    def get_filename(self):
        filename = get_filename_part(
            self.file_path, FileNamePart.WITHOUT_EXTENSION
        )
        log.info(f"Filename extracted: {filename}")
        return filename
