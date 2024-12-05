import sys
import os

# Add the project root to sys.path
current_dir = os.path.dirname(
    os.path.abspath(__file__)
)  # Directory of main.py
project_root = os.path.abspath(os.path.join(current_dir, ".."))  # One level up
sys.path.append(project_root)

# Now you can import config
from config.settings import CONFIG_DIR, CONFIG_FILES_DIR

from config.config_loader import load_enums


def start():
    # Load the configuration
    config = load_enums(yaml_dir=CONFIG_FILES_DIR)


if __name__ == "__main__":
    start()
