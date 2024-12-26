from functools import wraps
from src.utils.logger import setup_logger
from src.processors.image.image_processor import ImageProcessor

log = setup_logger(__name__)


def flatten_data(func):
    def flatten(nested_list):
        flat_list = []
        for item in nested_list:
            if isinstance(item, list):
                flat_list.extend(flatten(item))
            else:
                flat_list.append(item)
        return flat_list

    @wraps(func)
    def wrapper(*args, **kwargs):
        log.debug("Setting up data flattening decorator")
        data = kwargs.get("data", None)
        log.debug(
            f"Starting data flattening for data: {data[:100]}..."
        )  # Log first 100 chars
        if data is None:
            log.error("No data provided")
            return None
        data = flatten(data)
        log.debug("Data flattened")
        kwargs["data"] = data
        return func(*args, **kwargs)

    return wrapper


def base64_decode(func):
    def convert_img_to_binary(data):
        for record in data:
            record["image"] = ImageProcessor.base64_to_image(
                base64_str=record["image"]
            )
        return data

    @wraps(func)
    def wrapper(*args, **kwargs):
        log.debug("Setting up base64 decoding decorator")
        data = kwargs.get("data", None)
        log.debug(
            f"Starting base64 decoding for data: {data[:100]}..."
        )  # Log first 100 chars
        if data is None:
            log.error("No data provided")
            return None
        data = convert_img_to_binary(data)
        log.debug("Data decoded")
        kwargs["data"] = data
        return func(*args, **kwargs)

    return wrapper
