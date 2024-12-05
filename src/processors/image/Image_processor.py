import fitz
import os
import pandas as pd
import re
import numpy as np
import cv2 as cv
from config.config_files.config import ImageProcess
from src.enums.enums import ImageType
import base64


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
        for existing_rect in coords_list:
            existing_x, existing_y, existing_w, existing_h = existing_rect
            # Check for area, position, and size similarity
            # if (abs(existing_area - area) < area_difference_threshold and
            if (
                abs(existing_x - x) < position_threshold
                and abs(existing_y - y) < position_threshold
                and abs(existing_w - w) < size_threshold
                and abs(existing_h - h) < size_threshold
            ):
                return True
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
        # Attempt to read the image
        if image is None:
            raise ValueError("Image not found or unsupported format.")

        # Convert to grayscale
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        # Apply Gaussian blur
        blurred = cv.GaussianBlur(gray, blur.KSIZE, blur.SIGMA_X)

        if type == ImageType.ROI_IMAGE:
            return blurred

        # Denoise the blurred image
        denoised_image = cv.fastNlMeansDenoising(
            src=blurred,
            dst=None,
            h=de_noise.H,
            templateWindowSize=de_noise.TEMPLATE_WINDOW_SIZE,
            searchWindowSize=de_noise.SEARCH_WINDOW_SIZE,
        )

        # Apply sharpening filter to enhance edges
        sharpening_kernel = np.array(kernel.ARRAY)  # Basic sharpening kernel
        sharpened_image = cv.filter2D(
            src=denoised_image,
            ddepth=filter2d.DDEPTH,
            kernel=sharpening_kernel,
        )

        # Apply thresholding
        _, thresh = cv.threshold(
            src=sharpened_image,
            thresh=threshold.THRESH,
            maxval=threshold.MAX_VALUE,
            type=threshold.THRESHOLD_TYPE,
        )

        # Morphological transformation to reduce noise
        kernel = np.ones((3, 3), np.uint8)
        noise_reduced = cv.morphologyEx(
            src=thresh, op=morphology.OPERATION, kernel=morphology.KERNEL
        )

        # Dilation
        kernel_dilate = cv.getStructuringElement(cv.MORPH_RECT, (2, 2))
        dilated = cv.erode(
            noise_reduced, kernel_dilate, iterations=erode.ITERATIONS
        )
        return dilated

    def _find_contours(self, image, blur, edge_detection, contourConfig):
        # check if image is Not None
        if image is None:
            raise FileNotFoundError(f"Could not read the image")

        # Step 1: Convert to grayscale
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        blurred = cv.GaussianBlur(gray, blur.KSIZE, blur.SIGMA_X)

        # Step 2: Apply edge detection
        edges = cv.Canny(
            blurred,
            edge_detection.Canny.THRESHOLD1,
            edge_detection.Canny.THRESHOLD2,
        )
        # Step 3: Find contours
        contours, _ = cv.findContours(
            edges, contourConfig.MODE, contourConfig.METHOD
        )
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
        ext='png',
    ):
        # Initialize variables for storing detected rectangles
        large_rectangles = []
        roi_images = []
        detected_passport = None
        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h

            # Filter by area and aspect ratio to detect only large rectangles
            if (
                min_area_threshold < area < max_area_threshold
                and min_aspect_ratio < aspect_ratio < max_aspect_ratio
            ):
                if type == ImageType.ROI_IMAGE:
                    # Check for duplicates based on area
                    duplicate = self._is_duplicate_coords(
                        coords_list=large_rectangles,
                        contour=contour,
                        position_threshold=position_threshold,
                        size_threshold=size_threshold,
                    )

                    if not duplicate:
                        large_rectangles.append((x, y, w, h))

                        # Draw the rectangle on the original image
                        cv.rectangle(
                            image,
                            (x, y),
                            (x + w, y + h),
                            color.GREEN,
                            color_width.WIDTH,
                        )
                        # Crop the rectangle from the original image
                        cropped_image = image[y : y + h, x : x + w]
                        roi_images.append(cropped_image)
                elif type == ImageType.PASSPORT:
                    detected_passport = image[y : y + h, x : x + w]
                    ext = ext if ext.startswith('.') else '.' + ext
                    success, binary_passport_image = cv.imencode(
                        ext=ext, img=detected_passport
                    )
                    if success:
                        return (
                            True,
                            binary_passport_image.tobytes(),
                        )  # Return binary data of the passport image
        if type == ImageType.ROI_IMAGE:
            return roi_images
        # elif type == ImageType.PASSPORT:
        print("No passport-sized photo detected.")
        return (
            False,
            None,
        )

    def extract_roi_from_image(self, image):
        try:
            # load config
            blur = self.blur.ImageRoi
            edge_detection = self.edge_detection.ImageRoi
            contours = self.contours.ImageRoi
            contour_area = self.contour_area.ImageRoi
            color = self.color
            color_width = self.color_width

            # find all the contours
            contours = self._find_contours(
                image=image,
                blur=blur,
                edge_detection=edge_detection,
                contourConfig=contours,
            )

            # Step 4: Loop through contours and filter based on area and shape
            roi_images = self._extract_images(
                image=image,
                type=ImageType.ROI_IMAGE,
                contours=contours,
                min_area_threshold=contour_area.MIN_AREA_THRESHOLD,
                max_area_threshold=contour_area.MAX_AREA_THRESHOLD,
                min_aspect_ratio=contour_area.MIN_ASPECT_RATIO,
                max_aspect_ratio=contour_area.MAX_ASPECT_RATIO,
                position_threshold=contour_area.POSITION_THRESHOLD,  # X, Y coordinate difference threshold
                size_threshold=contour_area.SIZE_THRESHOLD,  # Width, Height difference threshold
                color=color,
                color_width=color_width,
            )

            return roi_images

        except FileNotFoundError as e:
            print(f"File not found error: {e}")
            return None
        except cv.error as e:
            print(f"OpenCV error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def extract_passport_photo(self, image, ext):
        # load config
        blur = self.blur.PassportBox
        edge_detection = self.edge_detection.PassportBox
        contours = self.contours.PassportBox
        contour_area = self.contour_area.PassportBox
        color = self.color
        color_width = self.color_width
        # load height and width
        height, width = image.shape[:2]

        # find all the contours
        contours = self._find_contours(
            image=image,
            blur=blur,
            edge_detection=edge_detection,
            contourConfig=contours,
        )
        passport_area = height * width

        return self._extract_images(
            image=image,
            type=ImageType.PASSPORT,
            contours=contours,
            min_area_threshold=passport_area
            * contour_area.MAX_AREA_RATIO,  # Set area threshold (e.g., 1% of image area)
            max_area_threshold=passport_area * contour_area.MAX_AREA_RATIO,
            min_aspect_ratio=contour_area.MIN_ASPECT_RATIO,
            max_aspect_ratio=contour_area.MAX_ASPECT_RATIO,
            position_threshold=contour_area.POSITION_THRESHOLD,  # X, Y coordinate difference threshold
            size_threshold=contour_area.SIZE_THRESHOLD,  # Width, Height difference threshold
            color=color,
            color_width=color_width,
            ext='png',
        )

    def image_to_base64(image, ext='png'):
        """
        Converts an image to a base64-encoded string.

        Args:
            image: The input image (NumPy array or None).
            ext: The image format (default: 'png').

        Returns:
            A base64-encoded string of the image, or None if the image is invalid.
        """
        try:
            if image is None:
                raise FileNotFoundError("The provided image is None.")

            # Encode the image to memory buffer as specified format (e.g., PNG)
            _, buffer = cv.imencode(f".{ext}", image)

            # Convert the image buffer to base64
            base64_str = base64.b64encode(buffer).decode('utf-8')
            return base64_str

        except FileNotFoundError as e:
            print(f"File not found error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def base64_to_image(base64_str):
        """
        Converts a Base64-encoded string to an OpenCV image (NumPy array).

        Args:
            base64_str: The Base64-encoded string of the image.

        Returns:
            An OpenCV image (NumPy array) if successful, None otherwise.
        """
        try:
            if not base64_str:
                raise ValueError(
                    "The provided Base64 string is empty or None."
                )

            # Decode the Base64 string to bytes
            image_bytes = base64.b64decode(base64_str)

            # Convert bytes to a NumPy array
            image_array = np.frombuffer(image_bytes, dtype=np.uint8)

            # Decode the NumPy array to an image using OpenCV
            image = cv.imdecode(image_array, cv.IMREAD_COLOR)

            if image is None:
                raise ValueError("The decoded image is invalid.")

            return image

        except ValueError as e:
            print(f"Value error: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

    def process_image(self, image):
        try:
            # load config
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
            )

            return processed_image

        except cv.error as e:
            print(f"OpenCV error occurred: {e}")
            return None, None
        except ValueError as e:
            print(f"Value error: {e}")
            return None, None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None
