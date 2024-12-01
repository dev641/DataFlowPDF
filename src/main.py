import sys
import os

# Add the project root to sys.path
current_dir = os.path.dirname(
    os.path.abspath(__file__)
)  # Directory of main.py
project_root = os.path.abspath(os.path.join(current_dir, ".."))  # One level up
sys.path.append(project_root)

# Now you can import config
from config.settings import CONFIG_DIR
