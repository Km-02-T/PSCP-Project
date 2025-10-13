import pytesseract
from PIL import Image

def extract_text(image_path):
    img = Image.open(image_path)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    texts = []
    for i in range(len(data["text"])):
        if int(data["conf"][i]) > 60 and data["text"][i].strip():
            texts.append(data["text"][i])
    return texts
