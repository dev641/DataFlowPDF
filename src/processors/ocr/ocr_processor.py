import pytesseract
import easyocr
from src.enums.enums import OcrEngine
from config.config_files.config import OcrProcess
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class OcrProcessor:
    def __init__(self, ocr_engine):
        log.info(f"Initializing OCR processor with engine: {ocr_engine}")
        self.ocr_engine = ocr_engine

        if ocr_engine == OcrEngine.PYTESSERACT:
            log.debug("Setting up Pytesseract configuration")
            self.config = OcrProcess.Pytesseract.Config
            self.lang = OcrProcess.Pytesseract.Lang
        elif ocr_engine == OcrEngine.EASYOCR:
            log.debug("Setting up EasyOCR configuration")
            self.config = OcrProcess.Easyocr.Config

        log.info("OCR processor initialization completed")

    def process_ocr(self, image, config, lang):
        """
        Process OCR on the given images using the selected OCR engine.
        """
        log.info(f"Starting OCR processing with {self.ocr_engine}")

        if self.ocr_engine == OcrEngine.PYTESSERACT:
            log.debug(f"Using Pytesseract with config: {config}, lang: {lang}")
            result = self._use_pytesseract(
                image=image, config=config, lang=lang
            )
            log.info("Pytesseract OCR processing completed")
            return result

        elif self.ocr_engine == OcrEngine.EASYOCR:
            log.debug("Using EasyOCR for processing")
            result = self._use_easyocr(image)
            log.info("EasyOCR processing completed")
            return result

        log.warning(f"Unsupported OCR engine: {self.ocr_engine}")
        return None

    def _use_pytesseract(self, image, config, lang):
        try:
            log.debug(
                f"Processing image with Pytesseract config={config}, lang={lang}"
            )
            text = pytesseract.image_to_string(
                image=image, config=config, lang=lang
            )
            log.info("Successfully extracted text using Pytesseract")
            return text
        except pytesseract.TesseractError as e:
            log.error(f"Error processing image with pytesseract: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error during OCR: {e}")
            return None

    def perform_ocr_on_sides(
        self, left_side, right_side, ocr_engine=OcrEngine.PYTESSERACT
    ):
        try:
            log.info("Starting OCR processing on image sides")
            # OCR configuration
            config = self.config.FIVE
            log.debug(f"Using OCR configuration: {config}")

            # Apply OCR to each part
            log.debug("Processing left side with HIN_ENG language")
            left_text = self._use_pytesseract(
                image=left_side, lang=self.lang.HIN_ENG, config=config
            )

            log.debug("Processing right side with ENGLISH language")
            right_text = self._use_pytesseract(
                image=right_side, lang=self.lang.ENGLISH, config=config
            )

            log.info("Successfully processed both sides with OCR")
            return left_text, right_text

        except Exception as e:
            log.error(f"Error during OCR processing: {e}")
            print(f"An error occurred during image processing: {e}")

    def _use_easyocr(self, image, lang):
        try:
            log.debug(f"Initializing EasyOCR reader with languages: {lang}")
            reader = easyocr.Reader(lang_list=lang)

            log.debug("Processing image with EasyOCR")
            result = reader.readtext(image)

            log.debug("Extracting text from EasyOCR results")
            detection = "\n".join([det[1] for det in result])

            log.info("Successfully completed EasyOCR text extraction")
            return detection

        except Exception as e:
            log.error(f"Error during EasyOCR processing: {e}")
            return None
