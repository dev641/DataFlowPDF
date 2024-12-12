from config.config_loader import load_json
import re


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def correct_misspelled_word(filePath):
    def decorator(func):
        def wrapper(data, *args, **kwargs):
            ocr_corrections = load_json(filePath=filePath)
            for key, val in ocr_corrections.items():
                for item in val:
                    data = data.replace(item, key)
            return func(data, *args, **kwargs)

        return wrapper

    return decorator


def normalize_text(func):
    def wrapper(data, *args, **kwargs):
        data = (
            data.replace(" : ", ":")
            .replace(": ", ":")
            .replace("::", ":")
            .split("\n")
        )
        return func(data, *args, **kwargs)


def hindi_to_english_digits(filePath):
    def decorator(func):
        def wrapper(data, *args, **kwargs):
            hindi_to_english_digits = load_json(filePath=filePath)
            data = ''.join(hindi_to_english_digits.get(ch, ch) for ch in data)
            return func(data, *args, **kwargs)

        return wrapper

    return decorator


def clean_empty_lines(func):
    def wrapper(data, *args, **kwargs):
        data = [line.strip() for line in data.split("\n") if line.strip()]
        return func("\n".join(data), *args, **kwargs)

    return wrapper


def format_pattern(pattern, replacement):
    def decorator(func):
        def wrapper(data, *args, **kwargs):
            data = re.sub(pattern=pattern, repl=replacement, string=data)
            return func(data, *args, **kwargs)

        return wrapper

    return decorator
