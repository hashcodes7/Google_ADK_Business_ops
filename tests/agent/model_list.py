import os
from pathlib import Path
import pytest
import requests


def get_api_key():
    return os.getenv("GOOGLE_API_KEY") or os.getenv("Gemini_API_KEY") or ""


def get_model():
    return os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")


def test_gemini_model_list():
    api_key = get_api_key()
    if not api_key:
        pytest.skip("No Google / Gemini API key found in active environment credentials.")

    url = "https://generativelanguage.googleapis.com/v1beta/models"

    try:
        response = requests.get(
            url,
            headers={"x-goog-api-key": api_key},
            params={"pageSize": 10},
            timeout=(10, 30),
        )
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
        models = [m.get("name", "").replace("models/", "") for m in response.json().get("models", [])]
        print(f"\n💚 [Result] Model catalog -> model_list.py -> GET /v1beta/models -> returned HTTP {response.status_code} ({len(models)} models available)")

    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Network error querying Gemini model list: {exc}")


if __name__ == "__main__":
    test_gemini_model_list()
