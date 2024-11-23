import pytesseract
import easyocr


class OcrProcessor:
    def __init__(self, ocr_engine='pytesseract'):
        self.ocr_engine = ocr_engine
    
    def process_ocr(self, image, config, lang):
        """
        Process OCR on the given images using the selected OCR engine.
        """
        if self.ocr_engine == 'pytesseract':
            print(f"Using {self.ocr_engine} for OCR processing on image: {image}")
            return self._use_pytesseract(image=image, config=config, lang=lang)
        elif self.ocr_engine == 'easyocr':
            print(f"Using {self.ocr_engine} for OCR processing on images: {image}")
            return self._use_easyocr(image)
        else:
            raise ValueError(f"Unsupported OCR engine: {self.ocr_engine}")
    
    def _use_pytesseract(self, image, config, lang):
        try:
            text = pytesseract.image_to_string(image=image, config=config, lang=lang)
            return text
        except pytesseract.TesseractError as e:
            print(f"Error processing image with pytesseract: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error ocurred during OCR:{e}")
            return None
        
    def _use_easyocr(self, image, config, lang):
        try:
            reader = easyocr.Reader(lang_list=lang)
            result = reader.readtext(image)
            detection = "\n".join([det[1] for det in result])
            return detection
        except Exception as e:
            print(f"An unexpected error ocurred during easyOCR:{e}")
            return None