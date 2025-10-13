import requests

def test_api():
    with open("test_images/sample.jpg", "rb") as f:
        response = requests.post(
            "http://localhost:8000/translate_image/",
            files={"file": f},
            params={"target_lang": "en"}
        )
    assert response.status_code == 200
