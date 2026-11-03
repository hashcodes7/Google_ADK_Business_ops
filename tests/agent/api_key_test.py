import os
from pathlib import Path
import pytest
import requests


def get_api_key():
    return os.getenv("GOOGLE_API_KEY") or os.getenv("Gemini_API_KEY") or ""


def test_gemini_api_key_connectivity():
    api_key = get_api_key()
    if not api_key:
        pytest.skip("No Google / Gemini API key found in active environment credentials.")

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent"
    )

    try:
        response = requests.post(
            url,
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": api_key,
            },
            json={
                "contents": [{
                    "parts": [{
                        "text": "Reply with: Gemini is working!"
                    }]
                }]
            },
            timeout=(15, 60),
        )
        assert response.status_code in (200, 429), f"Unexpected status code: {response.status_code}"
    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Network error connecting to Gemini API: {exc}")


if __name__ == "__main__":
    test_gemini_api_key_connectivity()
