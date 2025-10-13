from googletrans import Translator

translator = Translator()

def translate_text(text: str, target_lang: str = "en"):
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        return f"Error: {e}"
