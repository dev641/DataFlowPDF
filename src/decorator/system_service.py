from src.controllers.systems.service_controller import ServiceManager
from functools import wraps
from src.utils.logger import setup_logger

log = setup_logger(__name__)


def start_service(service_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log.info(f"Starting service: {service_name}")
            service_manager = ServiceManager()
            service_manager.start_service(service_name)
            log.debug(f"Service {service_name} started successfully")
            result = func(*args, **kwargs)
            log.info(
                f"Function {func.__name__} executed with service {service_name}"
            )
            return result

        return wrapper

    return decorator
