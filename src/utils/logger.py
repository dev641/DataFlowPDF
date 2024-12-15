import logging


def setup_logger(name: str, log_file: str = 'app.log'):
    logger = logging.getLogger(name)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
    return logger
