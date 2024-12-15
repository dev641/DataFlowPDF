import fitz
from PIL import Image
from config.settings import IMAGE_DPI, IMAGE_MODE
import numpy as np


class PdfReader:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_pdf(self):
        try:
            with fitz.open(self.file_path) as pdf:
                return pdf
        except fitz.FileDataError:
            print(f"Error: Invalid or corrupted PDF file: {self.file_path}")
            return None
        except FileNotFoundError:
            print(f"Error: PDF file not found: {self.file_path}")
            return None
        except Exception as e:
            print(f"Error reading PDF file {self.file_path}: {str(e)}")
            return None

    def _get_page_from_pdf(self, pdf, page_num):
        try:
            return pdf[page_num]
        except IndexError:
            print(f"Error: Page number {page_num} is out of range")
            return None
        except ValueError:
            print(f"Error: Invalid page number {page_num}")
            return None
        except Exception as e:
            print(f"Error accessing page {page_num}: {str(e)}")
            return None

    def extract_image_from_pdf(self, pdf, page_num):
        try:
            page = self._get_page_from_pdf(pdf=pdf, page_num=page_num)
            if page is None:
                return None

            pix = page.get_pixmap(dpi=IMAGE_DPI)
            img = Image.frombytes(
                IMAGE_MODE, [pix.width, pix.height], pix.samples
            )
            img_np = np.array(img)
            return img_np

        except AttributeError:
            print(f"Error: Invalid page object or missing pixmap method")
            return None
        except ValueError:
            print(f"Error: Invalid image data or conversion failed")
            return None
        except Exception as e:
            print(f"Error extracting image from PDF page {page_num}: {str(e)}")
            return None
