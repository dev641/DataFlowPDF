import fitz
import os
import pandas as pd
import re
import numpy as np
import cv2 as cv


class ImageProcessor:
    def __init__(self):
        pass

    def extract_roi_from_image(image):
        try:
            # Ensure the output directory exists
            # os.makedirs(roi_path, exist_ok=True)

            # Load the image
            # image = cv.imread(image_path)
            if image is None:
                raise FileNotFoundError(f"Could not read the image")

            # Step 1: Convert to grayscale
            gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            blurred = cv.GaussianBlur(gray, (13, 13), 0)

            # Step 2: Apply edge detection
            edges = cv.Canny(blurred, 50, 150)

            # Step 3: Find contours
            contours, _ = cv.findContours(
                edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE
            )

            # Initialize variables for storing detected rectangles
            large_rectangles = []
            roi_images = []
            crop_counter = 1
            position_threshold = 500  # X, Y coordinate difference threshold
            size_threshold = 200  # Width, Height difference threshold
            min_area_threshold = 2000000
            max_area_threshold = 3000000
            min_aspect_ratio = 2.4
            max_aspect_ratio = 2.6

            # Step 4: Loop through contours and filter based on area and shape
            for contour in contours:
                x, y, w, h = cv.boundingRect(contour)
                area = w * h
                aspect_ratio = w / h

                # Filter by area and aspect ratio to detect only large rectangles
                if (
                    min_area_threshold < area < max_area_threshold
                    and min_aspect_ratio < aspect_ratio < max_aspect_ratio
                ):
                    # Check for duplicates based on area
                    duplicate = is_duplicate_coords(
                        coords_list=large_rectangles,
                        contour=contour,
                        position_threshold=position_threshold,
                        size_threshold=size_threshold,
                    )

                    if not duplicate:
                        large_rectangles.append((x, y, w, h))

                        # Draw the rectangle on the original image
                        cv.rectangle(
                            image, (x, y), (x + w, y + h), (0, 255, 0), 20
                        )
                        # Crop the rectangle from the original image
                        cropped_image = image[y : y + h, x : x + w]
                        roi_images.append(cropped_image)
                        # image_name = get_filename_part(image_path, part=FileNamePart.WITHOUT_EXTENSION)

                        # # Save the cropped image
                        # cropped_image_path = f"{roi_path}/{image_name}_roi_{crop_counter}.png"
                        # cv.imwrite(cropped_image_path, cropped_image)
                        # crop_counter += 1

            # Optionally, save or display the result
            # cv.imwrite(f"processed_{os.path.basename(image_path)}", image)

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


# Example usage
# large_rectangles = extract_roi_from_image(image_path="images/page.png", roi_path="images/roi")

# extract_roi_from_image(image_path="images/2024-FC-EROLLGEN-S04-196-FinalRoll-Revision5-HIN-1/page_3.png", roi_path="images/roi")
