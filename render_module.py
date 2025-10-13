from PIL import Image, ImageDraw, ImageFont
import os

def render_translated_text(image_path, text_pairs):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        font = ImageFont.load_default()

    y = 30
    for original, translated in text_pairs:
        draw.text((20, y), translated, fill=(255, 0, 0), font=font)
        y += 30

    output_path = os.path.splitext(image_path)[0] + "_translated.jpg"
    img.save(output_path)
    return output_path
