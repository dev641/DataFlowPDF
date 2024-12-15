import pytesseract
import easyocr
from src.enums.enums import OcrEngine
from config.config_files.config import OcrProcess


class OcrProcessor:
    def __init__(self, ocr_engine):
        self.ocr_engine = ocr_engine
        if ocr_engine == OcrEngine.PYTESSERACT:
            self.config = OcrProcess.Pytesseract.Config
            self.lang = OcrProcess.Pytesseract.Lang
        elif ocr_engine == OcrEngine.EASYOCR:
            self.config = OcrProcess.Easyocr.Config
            self.lang = OcrProcess.Easyocr.Lang

    def process_ocr(self, image, config, lang):
        """
        Process OCR on the given images using the selected OCR engine.
        """
        if self.ocr_engine == OcrEngine.PYTESSERACT:
            print(
                f"Using {self.ocr_engine} for OCR processing on image: {image}"
            )
            return self._use_pytesseract(image=image, config=config, lang=lang)
        elif self.ocr_engine == OcrEngine.EASYOCR:
            print(
                f"Using {self.ocr_engine} for OCR processing on images: {image}"
            )
            return self._use_easyocr(image)
        else:
            raise ValueError(f"Unsupported OCR engine: {self.ocr_engine}")

    def _use_pytesseract(self, image, config, lang):
        try:
            text = pytesseract.image_to_string(
                image=image, config=config, lang=lang
            )
            return text
        except pytesseract.TesseractError as e:
            print(f"Error processing image with pytesseract: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during OCR:{e}")
            return None

    def perform_ocr_on_sides(
        self, left_side, right_side, ocr_engine=OcrEngine.PYTESSERACT
    ):
        try:

            # OCR configuration
            config = self.config.FIVE

            # Apply OCR to each part
            left_text = self._use_pytesseract(
                image=left_side, lang=self.lang.HIN_ENG, config=config
            )
            right_text = self._use_pytesseract(
                image=right_side, lang=self.lang.ENGLISH, config=config
            )

            # Combine left and right text
            return left_text, right_text  # Merging the dictionaries

        except Exception as e:
            # Handle any errors that occur during processing
            print(f"An error occurred during image processing: {e}")
            return {}, {}  # Return an empty dictionary if an error occurs

    def _use_easyocr(self, image, lang):
        try:
            reader = easyocr.Reader(lang_list=lang)
            result = reader.readtext(image)
            detection = "\n".join([det[1] for det in result])
            return detection
        except Exception as e:
            print(f"An unexpected error occurred during easyOCR:{e}")
            return None
