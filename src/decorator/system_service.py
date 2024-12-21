from src.controllers.systems.service_controller import ServiceManager
from functools import wraps


def start_service(service_name):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            service_manager = ServiceManager()
            service_manager.start_service(service_name)
            return func(*args, **kwargs)

        return wrapper

    return decorator
