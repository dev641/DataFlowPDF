from enum import Enum
import cv2 as cv


class ImageProcess:
    class Counters:
        class ImageRoi:
            MODE = cv.RETR_EXTERNAL
            METHOD = cv.CHAIN_APPROX_SIMPLE

        class PassportBox:
            MODE = cv.RETR_TREE
            METHOD = cv.CHAIN_APPROX_SIMPLE

    class Blur:
        class ImageRoi:
            KSIZE = (13, 13)
            SIGMA_X = 0

        class ProcessRoi:
            KSIZE = (13, 13)
            SIGMA_X = 0

        class PassportBox:
            KSIZE = (5, 5)
            SIGMA_X = 0

    class DeNoise:
        class ProcessRoi:
            H = 30
            TEMPLATE_WINDOW_SIZE = 7
            SEARCH_WINDOW_SIZE = 21

    class Kernel:
        class ProcessRoi:
            ARRAY = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]

    class Filter2d:
        class ProcessRoi:
            DDEPTH = -1

    class EdgeDetection:
        class ImageRoi:
            class Canny:
                THRESHOLD1 = 50
                THRESHOLD2 = 150

        class PassportBox:
            class Canny:
                THRESHOLD1 = 50
                THRESHOLD2 = 150

    class ContourArea:
        class ImageRoi:
            POSITION_THRESHOLD = 500
            SIZE_THRESHOLD = 200
            MIN_AREA_THRESHOLD = 2000000
            MAX_AREA_THRESHOLD = 3000000
            MIN_ASPECT_RATIO = 2.4
            MAX_ASPECT_RATIO = 2.6

        class PassportBox:
            MIN_AREA_RATIO = 0.05
            MAX_AREA_RATIO = 0.15
            MIN_ASPECT_RATIO = 0.7
            MAX_ASPECT_RATIO = 1.5

    class Threshold:
        class ProcessRoi:
            THRESH = 100
            MAX_VALUE = 255
            THRESHOLD_TYPE = cv.THRESH_BINARY + cv.THRESH_OTSU

    class Morphology:
        class ProcessRoi:
            KERNEL = (3, 3)
            OPERATION = cv.MORPH_CLOSE

    class Erode:
        class ProcessRoi:
            ITERATIONS = 1

    class Color:
        GREEN = (0, 255, 0)
        BLUE = (255, 0, 0)
        RED = (0, 0, 255)

    class Border:
        WIDTH = 20


class OcrProcess:
    OCR_ENGINE = ['PYTESSERACT', 'EASYOCR']

    class Pytesseract:
        class Config:
            DEFAULT = ''
            ONE = '--psm 6 --oem 3'
            TWO = '--psm 6 --oem 3'
            THREE = '--psm 6 --oem 3'
            FOUR = '--psm 6 --oem 3'
            FIVE = '--psm 3 --dpi 600'

        class Lang:
            ENGLISH = 'eng'
            HINDI = 'hin'
            HIN_ENG = 'hin+eng'
            ENGLISH_HINDI = 'eng+hin'

    class Easyocr:
        class Lang:
            ENGLISH = 'en'
            HINDI = 'hi'
            HIN_ENG = 'hi+en'
            ENGLISH_HINDI = 'en+hi'
