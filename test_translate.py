from backend.translate_module import translate_text

def test_translation():
    result = translate_text("สวัสดี", "en")
    assert isinstance(result, str)
