import os
from pathlib import Path
import pytest
import requests


def get_api_key():
    return os.getenv("GOOGLE_API_KEY") or os.getenv("Gemini_API_KEY") or ""


def test_gemini_model_list():
    api_key = get_api_key()
    if not api_key:
        pytest.skip("No Google / Gemini API key found in active environment credentials.")

    url = "https://generativelanguage.googleapis.com/v1beta/models"

    try:
        response = requests.get(
            url,
            headers={"x-goog-api-key": api_key},
            params={"pageSize": 5},
            timeout=(10, 30),
        )
        assert response.status_code in (200, 429), f"Unexpected status code: {response.status_code}"
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Network error querying Gemini model list: {exc}")


if __name__ == "__main__":
    test_gemini_model_list()
