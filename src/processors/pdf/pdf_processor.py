from .pdf_reader import PdfReader
from ..image.image_processor import ImageProcessor
from ..ocr.ocr_processor import OcrProcessor
from ..text.text_processor import TextProcessor
from src.enums.enums import OcrEngine
from config.config_files.config import ImageProcess
from config.settings import START_PAGE, PAGE_TO_EXCLUDE
from utils.file_saver import FileSaver


class PdfProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_reader = PdfReader(self.pdf_path)
        self.ocr_processor = OcrProcessor(ocr_engine=OcrEngine.PYTESSERACT)
        self.image_processor = ImageProcessor(
            blur=ImageProcess.Blur,
            edge_detection=ImageProcess.EdgeDetection,
            contours=ImageProcess.Counters,
            contour_area=ImageProcess.ContourArea,
            de_noise=ImageProcess.DeNoise,
            kernel=ImageProcess.Kernel,
            filter2d=ImageProcess.Filter2d,
            threshold=ImageProcess.Threshold,
            morphology=ImageProcess.Morphology,
            erode=ImageProcess.Erode,
            color=ImageProcess.Color,
            color_width=ImageProcess.Border,
        )

    def _process_roi_and_extract_text(self, roi_image):
        left_side, right_side = self.image_processor.split_roi_into_sides(
            image=roi_image
        )
        left_text, right_text = self.ocr_processor.extract_text_from_roi(
            left_side, right_side
        )

        left_text = TextProcessor.format_text(left_text) or {}
        right_text = TextProcessor.format_text(right_text) or {}

        return left_text | right_text

    def extract_information_from_all_roi(
        self, roi_images, image_processor: ImageProcessor
    ):
        try:
            data = []
            for roi in roi_images:
                try:
                    text = self._process_roi_and_extract_text(roi_image=roi)
                    is_photo_detected, image = (
                        image_processor.extract_passport_image_in_base64_format(
                            roi=roi
                        )
                    )
                    if is_photo_detected:
                        text["image"] = image
                    data.append(text)
                except Exception as e:
                    print(f"Error processing individual ROI: {str(e)}")
                    continue
            return data
        except ValueError:
            print("Error: Invalid ROI images provided")
            return []
        except Exception as e:
            print(f"Error processing ROIs: {str(e)}")
            return []

    def save_voter_information_from_pdf(
        self, start_page=START_PAGE, pages_to_exclude=PAGE_TO_EXCLUDE
    ):
        pdf_reader = self.pdf_reader
        image_processor = self.image_processor
        voter_data = []
        pdf = pdf_reader.read_pdf()
        for page_num in range(start_page, pdf.page_count - pages_to_exclude):
            image = pdf_reader.extract_image_from_pdf(
                pdf=pdf, page_num=page_num
            )
            roi_images = image_processor.extract_roi_from_image(image=image)
            data = self.extract_information_from_all_roi(
                roi_images=roi_images, image_processor=image_processor
            )
            # Process the data as needed
            # ...
            voter_data.append(data)
        FileSaver.save_data(data=voter_data, file_name="voter_data")
