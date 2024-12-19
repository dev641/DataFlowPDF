from multiprocessing import Pool, cpu_count
from functools import partial
from .pdf_reader import PdfReader
from ..image.image_processor import ImageProcessor
from ..ocr.ocr_processor import OcrProcessor
from ..text.text_processor import TextProcessor
from src.enums.enums import OcrEngine, ImageType
from config.config_files.config import ImageProcess
from config.settings import START_PAGE, PAGE_TO_EXCLUDE
from src.utils.file_saver import FileSaver
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class PdfProcessor:
    def __init__(self, pdf_path):
        log.info(f"Initializing PDF processor for: {pdf_path}")

        log.debug("Setting up PDF path")
        self.pdf_path = pdf_path

        log.debug("Initializing PDF reader")
        self.pdf_reader = PdfReader(self.pdf_path)

        log.debug("Setting up OCR processor with Pytesseract engine")
        self.ocr_processor = OcrProcessor(ocr_engine=OcrEngine.PYTESSERACT)

        log.debug("Configuring image processor with processing parameters")
        self.image_processor = ImageProcessor(
            blur=ImageProcess.Blur,
            edge_detection=ImageProcess.EdgeDetection,
            contours=ImageProcess.Counters,
            contour_area=ImageProcess.ContourArea,
            de_noise=ImageProcess.DeNoise,
            kernel=ImageProcess.Kernel,
            filter2d=ImageProcess.Filter2D,
            threshold=ImageProcess.Threshold,
            morphology=ImageProcess.Morphology,
            erode=ImageProcess.Erode,
            color=ImageProcess.Color,
            color_width=ImageProcess.Border,
        )
        log.info("PDF processor initialization completed")

    def _process_roi_and_extract_text(self, roi_image):
        log.info("Starting ROI text extraction process")

        log.debug("Processing ROI image")
        processed_roi = self.image_processor.process_image(
            roi_image, type=ImageType.ROI_IMAGE
        )

        log.debug("Splitting ROI into sides")
        left_side, right_side = self.image_processor.split_roi_into_sides(
            processed_roi
        )

        log.debug("Performing OCR on both sides")
        left_text, right_text = self.ocr_processor.perform_ocr_on_sides(
            left_side=left_side,
            right_side=right_side,
            ocr_engine=OcrEngine.PYTESSERACT,
        )

        log.debug("Processing left side text")
        left_text = TextProcessor.format_text(left_text)

        log.debug("Processing right side text")
        right_text = TextProcessor.format_text(right_text)

        log.debug("Merging text from both sides")
        text = {**left_text, **right_text}

        log.info("Successfully completed ROI text extraction")
        return text

    def extract_information_from_all_roi(
        self, roi_images, image_processor: ImageProcessor
    ):
        log.info("Starting information extraction from ROIs")
        data = []

        for roi in roi_images:
            log.debug("Processing individual ROI")
            text = self._process_roi_and_extract_text(roi_image=roi)

            log.debug("Attempting to extract passport image")
            is_photo_detected, image = (
                image_processor.extract_passport_image_in_base64_format(
                    roi=roi
                )
            )

            if is_photo_detected:
                log.info("Passport photo detected and extracted")
                text["image"] = image

            data.append(text)

        log.info(f"Completed processing {len(roi_images)} ROIs")
        return data

    def _process_single_page(self, args):
        pdf_path, page_num, config = args

        # Create new instances for each process
        pdf_reader = PdfReader(pdf_path)
        image_processor = ImageProcessor(
            blur=config.Blur,
            edge_detection=config.EdgeDetection,
            contours=config.Counters,
            contour_area=config.ContourArea,
            de_noise=config.DeNoise,
            kernel=config.Kernel,
            filter2d=config.Filter2D,
            threshold=config.Threshold,
            morphology=config.Morphology,
            erode=config.Erode,
            color=config.Color,
            color_width=config.Border,
        )

        # Get PDF object for this process
        pdf = pdf_reader.process_pdf(lambda x: x)
        image = pdf_reader.extract_image_from_pdf(pdf=pdf, page_num=page_num)
        roi_images = image_processor.extract_roi_from_image(image=image)
        return self.extract_information_from_all_roi(
            roi_images=roi_images, image_processor=image_processor
        )

    # def _process_pdf(self, pdf, start_page, pages_to_exclude):
    #     voter_data = []

    #     if pdf:
    #         log.info(
    #             f"Processing pages from {start_page} to {pdf.page_count - pages_to_exclude}"
    #         )

    #         # Pass pdf_path instead of pdf_reader instance
    #         page_args = [
    #             (self.pdf_path, page_num, ImageProcess)
    #             for page_num in range(
    #                 start_page, pdf.page_count - pages_to_exclude
    #             )
    #         ]

    #         with Pool(processes=cpu_count()) as pool:
    #             # Use partial to bind self to the method
    #             bound_process = partial(self._process_single_page)
    #             voter_data = pool.map(bound_process, page_args)

    #         log.info(f"Successfully processed {len(voter_data)} pages")
    #         FileSaver.save_data(data=voter_data, file_name="voter_data")
    #     log.info("Voter data saved successfully")

    def _process_pdf(self, pdf, start_page, pages_to_exclude):
        pdf_reader = self.pdf_reader
        image_processor = self.image_processor
        voter_data = []
        if pdf:
            log.info(
                f"Processing pages from {start_page} to {pdf.page_count - pages_to_exclude}"
            )
            for page_num in range(
                start_page, pdf.page_count - pages_to_exclude
            ):
                log.debug(f"Processing page {page_num}")

                image = pdf_reader.extract_image_from_pdf(
                    pdf=pdf, page_num=page_num
                )
                log.debug(f"Extracting ROIs from page {page_num}")
                roi_images = image_processor.extract_roi_from_image(
                    image=image
                )

                log.debug(
                    f"Extracting information from ROIs on page {page_num}"
                )
                data = self.extract_information_from_all_roi(
                    roi_images=roi_images, image_processor=image_processor
                )
                voter_data.append(data)

            log.info(f"Successfully processed {len(voter_data)} pages")
            FileSaver.save_data(data=voter_data, file_name="voter_data")
            log.info("Voter data saved successfully")

    def save_voter_information_from_pdf(
        self, start_page=START_PAGE, pages_to_exclude=PAGE_TO_EXCLUDE
    ):
        log.info(
            f"Starting voter information extraction from PDF: {self.pdf_path}"
        )

        pdf_reader = self.pdf_reader
        log.debug("Reading PDF file")
        pdf = pdf_reader.process_pdf(
            lambda pdf: self._process_pdf(pdf, start_page, pages_to_exclude)
        )
