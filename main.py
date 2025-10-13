from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from ocr_module import extract_text
from translate_module import translate_text
from render_module import render_translated_text
from utils import setup_logger, create_upload_folder
import shutil

app = FastAPI()
setup_logger()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = create_upload_folder()

@app.post("/translate_image/")
async def translate_image(file: UploadFile, target_lang: str = "en"):
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text_data = extract_text(file_path)
    translated_data = [(text, translate_text(text, target_lang)) for text in text_data]
    output_path = render_translated_text(file_path, translated_data)

    return {
        "translated_image": output_path,
        "text_data": translated_data
    }
