import os
import logging

def setup_logger():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )

def create_upload_folder(path="uploads"):
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def allowed_file(filename):
    return filename.lower().endswith(('.png', '.jpg', '.jpeg'))
