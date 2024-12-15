import fitz
import os
import pandas as pd
import re
import numpy as np
import cv2 as cv
from config.config_files.config import ImageProcess
from src.enums.enums import ImageType, ImageExtensions
import base64
from config.settings import NUM_SECTION
from utils.logger import setup_logger

log = setup_logger(__name__)


class ImageProcessor:

    def __init__(
        self,
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
    ):
        self.blur = blur
        self.edge_detection = edge_detection
        self.contours = contours
        self.contour_area = contour_area
        self.de_noise = de_noise
        self.kernel = kernel
        self.filter2d = filter2d
        self.threshold = threshold
        self.morphology = morphology
        self.erode = erode
        self.color = color
        self.color_width = color_width

    def _is_duplicate_coords(
        self, coords_list, contour, position_threshold=500, size_threshold=200
    ):
        x, y, w, h = cv.boundingRect(contour)
        # Only detailed coordinates in DEBUG level
        log.debug(f"Checking contour bounds: x={x}, y={y}, w={w}, h={h}")

        for existing_rect in coords_list:
            existing_x, existing_y, existing_w, existing_h = existing_rect
            # Comparison details only in DEBUG
            log.debug(
                f"Comparing with existing rect: x={existing_x}, y={existing_y}, w={existing_w}, h={existing_h}"
            )

            if (
                abs(existing_x - x) < position_threshold
                and abs(existing_y - y) < position_threshold
                and abs(existing_w - w) < size_threshold
                and abs(existing_h - h) < size_threshold
            ):
                # Important events in INFO
                log.info("Duplicate coordinates found")
                return True

        # Process completion in DEBUG
        log.debug("No duplicate coordinates found")
        return False

    def _process_image(
        self,
        image,
        blur,
        de_noise,
        kernel,
        filter2d,
        threshold,
        morphology,
        erode,
        type=ImageType.PASSPORT,
    ):
        log.info(f"Processing image with type: {type}")

        if image is None:
            log.error("Image not found or unsupported format")
            raise ValueError("Image not found or unsupported format.")

        # Convert to grayscale
        log.debug("Converting image to grayscale")
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        log.debug(
            f"Applying Gaussian blur with ksize={blur.KSIZE}, sigma={blur.SIGMA_X}"
        )
        blurred = cv.GaussianBlur(gray, blur.KSIZE, blur.SIGMA_X)

        if type == ImageType.ROI_IMAGE:
            log.info("ROI image processing completed")
            return blurred

        # Denoise the blurred image
        log.debug("Applying denoising with parameters: h={de_noise.H}")
        denoised_image = cv.fastNlMeansDenoising(
            src=blurred,
            dst=None,
            h=de_noise.H,
            templateWindowSize=de_noise.TEMPLATE_WINDOW_SIZE,
            searchWindowSize=de_noise.SEARCH_WINDOW_SIZE,
        )

        # Apply sharpening filter
        log.debug("Applying sharpening filter")
        sharpening_kernel = np.array(kernel.ARRAY)
        sharpened_image = cv.filter2D(
            src=denoised_image,
            ddepth=filter2d.DDEPTH,
            kernel=sharpening_kernel,
        )

        # Apply thresholding
        log.debug(f"Applying threshold with value={threshold.THRESH}")
        _, thresh = cv.threshold(
            src=sharpened_image,
            thresh=threshold.THRESH,
            maxval=threshold.MAX_VALUE,
            type=threshold.THRESHOLD_TYPE,
        )

        # Morphological transformation
        log.debug("Applying morphological transformation")
        kernel = np.ones((3, 3), np.uint8)
        noise_reduced = cv.morphologyEx(
            src=thresh, op=morphology.OPERATION, kernel=morphology.KERNEL
        )

        # Dilation
        log.debug(f"Applying erosion with iterations={erode.ITERATIONS}")
        kernel_dilate = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
        dilated = cv.erode(
            noise_reduced, kernel_dilate, iterations=erode.ITERATIONS
        )

        log.info("Image processing completed successfully")
        return dilated

    def _find_contours(self, image, blur, edge_detection, contourConfig):
        log.info("Starting contour detection process")

        if image is None:
            log.error("Could not read the image")
            raise FileNotFoundError(f"Could not read the image")

        # Step 1: Convert to grayscale
        log.debug("Converting image to grayscale")
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        log.debug(f"Applying Gaussian blur with ksize={blur.KSIZE}")
        blurred = cv.GaussianBlur(gray, blur.KSIZE, blur.SIGMA_X)

        # Step 2: Apply edge detection
        log.debug(
            f"Applying Canny edge detection with thresholds: {edge_detection.Canny.THRESHOLD1}, {edge_detection.Canny.THRESHOLD2}"
        )
        edges = cv.Canny(
            blurred,
            edge_detection.Canny.THRESHOLD1,
            edge_detection.Canny.THRESHOLD2,
        )

        # Step 3: Find contours
        log.debug(f"Finding contours with mode={contourConfig.MODE}")
        contours, _ = cv.findContours(
            edges, contourConfig.MODE, contourConfig.METHOD
        )

        log.info(f"Found {len(contours)} contours")
        return contours

    def _extract_images(
        self,
        image,
        type,
        contours,
        min_area_threshold,
        max_area_threshold,
        min_aspect_ratio,
        max_aspect_ratio,
        position_threshold,
        size_threshold,
        color,
        color_width,
        ext=ImageExtensions.PNG.get_extension(),
    ):
        log.info(f"Starting image extraction for type: {type}")
        log.debug(f"Processing {len(contours)} contours")

        large_rectangles = []
        roi_images = []
        detected_passport = None

        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h

            log.debug(
                f"Contour metrics - Area: {area}, Aspect ratio: {aspect_ratio}"
            )

            if (
                min_area_threshold < area < max_area_threshold
                and min_aspect_ratio < aspect_ratio < max_aspect_ratio
            ):
                if type == ImageType.ROI_IMAGE:
                    log.debug("Processing ROI image type")
                    duplicate = self._is_duplicate_coords(
                        coords_list=large_rectangles,
                        contour=contour,
                        position_threshold=position_threshold,
                        size_threshold=size_threshold,
                    )

                    if not duplicate:
                        log.debug(
                            f"Adding new rectangle at x={x}, y={y}, w={w}, h={h}"
                        )
                        large_rectangles.append((x, y, w, h))

                        cv.rectangle(
                            image,
                            (x, y),
                            (x + w, y + h),
                            color.GREEN,
                            color_width.WIDTH,
                        )
                        cropped_image = image[y : y + h, x : x + w]
                        roi_images.append(cropped_image)

                elif type == ImageType.PASSPORT:
                    log.debug("Processing passport image type")
                    detected_passport = image[y : y + h, x : x + w]
                    success, binary_passport_image = cv.imencode(
                        ext=ext, img=detected_passport
                    )
                    if success:
                        log.info("Successfully encoded passport image")
                        return True, binary_passport_image.tobytes()

        if type == ImageType.ROI_IMAGE:
            log.info(f"Extracted {len(roi_images)} ROI images")
            return roi_images

        log.warning("No passport-sized photo detected")
        return False, None

    def extract_roi_from_image(self, image):
        log.info("Starting ROI extraction process")
        try:
            # load config
            log.debug("Loading ROI configuration parameters")
            blur = self.blur.ImageRoi
            edge_detection = self.edge_detection.ImageRoi
            contours = self.contours.ImageRoi
            contour_area = self.contour_area.ImageRoi
            color = self.color
            color_width = self.color_width

            # find all the contours
            log.debug("Finding contours in image")
            contours = self._find_contours(
                image=image,
                blur=blur,
                edge_detection=edge_detection,
                contourConfig=contours,
            )

            log.debug("Extracting ROI images from contours")
            roi_images = self._extract_images(
                image=image,
                type=ImageType.ROI_IMAGE,
                contours=contours,
                min_area_threshold=contour_area.MIN_AREA_THRESHOLD,
                max_area_threshold=contour_area.MAX_AREA_THRESHOLD,
                min_aspect_ratio=contour_area.MIN_ASPECT_RATIO,
                max_aspect_ratio=contour_area.MAX_ASPECT_RATIO,
                position_threshold=contour_area.POSITION_THRESHOLD,
                size_threshold=contour_area.SIZE_THRESHOLD,
                color=color,
                color_width=color_width,
            )

            log.info(
                f"Successfully extracted {len(roi_images) if roi_images else 0} ROI images"
            )
            return roi_images

        except FileNotFoundError as e:
            log.error(f"File not found error: {e}")
            return None
        except cv.error as e:
            log.error(f"OpenCV error: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error during ROI extraction: {e}")
            return None

    def _extract_passport_photo(
        self, image, ext=ImageExtensions.PNG.get_extension()
    ):
        log.info("Starting passport photo extraction")

        # load config
        log.debug("Loading passport box configuration")
        blur = self.blur.PassportBox
        edge_detection = self.edge_detection.PassportBox
        contours = self.contours.PassportBox
        contour_area = self.contour_area.PassportBox
        color = self.color
        color_width = self.color_width

        # load height and width
        height, width = image.shape[:2]
        log.debug(f"Image dimensions: {width}x{height}")

        # find all the contours
        log.debug("Finding contours for passport detection")
        contours = self._find_contours(
            image=image,
            blur=blur,
            edge_detection=edge_detection,
            contourConfig=contours,
        )
        passport_area = height * width
        log.debug(f"Total passport area: {passport_area}")

        log.debug("Extracting passport image")
        return self._extract_images(
            image=image,
            type=ImageType.PASSPORT,
            contours=contours,
            min_area_threshold=passport_area * contour_area.MAX_AREA_RATIO,
            max_area_threshold=passport_area * contour_area.MAX_AREA_RATIO,
            min_aspect_ratio=contour_area.MIN_ASPECT_RATIO,
            max_aspect_ratio=contour_area.MAX_ASPECT_RATIO,
            position_threshold=contour_area.POSITION_THRESHOLD,
            size_threshold=contour_area.SIZE_THRESHOLD,
            color=color,
            color_width=color_width,
            ext=ext,
        )

    def extract_passport_image_in_base64_format(self, roi):
        log.info("Starting passport image base64 conversion")
        try:
            log.debug("Extracting passport photo")
            is_success, binary_image = self._extract_passport_photo(roi)

            if is_success:
                log.debug("Converting passport photo to base64")
                result = self.image_to_base64(
                    binary_image, ext=ImageExtensions.PNG.get_extension()
                )
                log.info("Successfully converted passport photo to base64")
                return is_success, result

            log.warning("No passport photo detected")
            return is_success, None

        except ValueError:
            log.error("Failed to extract passport photo from ROI")
            return None
        except Exception as e:
            log.error(f"Error converting passport photo to base64: {str(e)}")
            return None

    def split_roi_into_sides(self, image, num_sections=NUM_SECTION):
        log.info("Starting ROI splitting process")
        _, width = image.shape[:num_sections]
        log.debug(f"Image width: {width}, Number of sections: {num_sections}")

        # Define the two regions by slicing the image
        left_side = image[:, : width // num_sections]  # Left half
        right_side = image[:, width // num_sections :]  # Right half

        log.info("Successfully split ROI into sides")
        return left_side, right_side

    def image_to_base64(image, ext=ImageExtensions.PNG.get_extension()):
        """
        Converts an image to a base64-encoded string.

        Args:
            image: The input image (NumPy array or None).
            ext: The image format (default: 'png').

        Returns:
            A base64-encoded string of the image, or None if the image is invalid.
        """
        log.info("Starting image to base64 conversion")
        try:
            if image is None:
                log.error("Invalid input: image is None")
                raise FileNotFoundError("The provided image is None.")

            log.debug(f"Encoding image with extension: {ext}")
            # Encode the image to memory buffer as specified format (e.g., PNG)
            _, buffer = cv.imencode(ext=ext, img=image)

            # Convert the image buffer to base64
            base64_str = base64.b64encode(buffer).decode('utf-8')
            log.info("Successfully converted image to base64")
            return base64_str

        except FileNotFoundError as e:
            log.error(f"File not found error: {e}")
            return None
        except Exception as e:
            log.error(f"Error in base64 conversion: {str(e)}")
            return None

    def base64_to_image(base64_str):
        """
        Converts a Base64-encoded string to an OpenCV image (NumPy array).

        Args:
            base64_str: The Base64-encoded string of the image.

        Returns:
            An OpenCV image (NumPy array) if successful, None otherwise.
        """
        log.info("Starting base64 to image conversion")
        try:
            if not base64_str:
                log.error("Invalid input: base64 string is empty or None")
                raise ValueError(
                    "The provided Base64 string is empty or None."
                )

            log.debug("Decoding base64 string to bytes")
            # Decode the Base64 string to bytes
            image_bytes = base64.b64decode(base64_str)

            log.debug("Converting bytes to NumPy array")
            # Convert bytes to a NumPy array
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)

            log.debug("Decoding NumPy array to OpenCV image")
            # Decode the NumPy array to an image using OpenCV
            image = cv.imdecode(image_array, cv.IMREAD_COLOR)

            if image is None:
                log.error("Failed to decode image from array")
                raise ValueError("The decoded image is invalid.")

            log.info("Successfully converted base64 to image")
            return image

        except ValueError as e:
            log.error(f"Value error: {e}")
            return None
        except Exception as e:
            log.error(f"Error in image conversion: {str(e)}")
            return None

    def process_image(self, image, type):
        log.info("Starting image processing")
        try:
            # load config
            log.debug("Loading configuration parameters")
            blur = self.blur.ImageRoi
            edge_detection = self.edge_detection.ImageRoi
            contours = self.contours.ImageRoi
            contour_area = self.contour_area.ImageRoi
            de_noise = self.de_noise.ProcessRoi
            kernel = self.kernel.ProcessRoi
            filter2d = self.filter2d.ProcessRoi
            threshold = self.threshold.ProcessRoi
            morphology = self.morphology.ProcessRoi
            erode = self.erode.ProcessRoi
            color = self.color
            color_width = self.color_width

            log.debug("Processing image with configured parameters")
            # process image
            processed_image = self._process_image(
                image=image,
                blur=blur,
                edge_detection=edge_detection,
                contours=contours,
                contour_area=contour_area,
                de_noise=de_noise,
                kernel=kernel,
                filter2d=filter2d,
                threshold=threshold,
                morphology=morphology,
                erode=erode,
                color=color,
                color_width=color_width,
                type=type,
            )

            log.info("Image processing completed successfully")
            return processed_image

        except cv.error as e:
            log.error(f"OpenCV error occurred: {e}")
            return None, None
        except ValueError as e:
            log.error(f"Value error: {e}")
            return None, None
        except Exception as e:
            log.error(f"Unexpected error in image processing: {e}")
            return None, None
