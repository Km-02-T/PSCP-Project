from backend.ocr_module import extract_text

def test_ocr_output():
    texts = extract_text("test_images/sample.jpg")
    assert isinstance(texts, list)
    assert all(isinstance(t, str) for t in texts)
