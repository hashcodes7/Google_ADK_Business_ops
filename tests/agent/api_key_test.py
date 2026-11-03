import os
from pathlib import Path
import pytest
import requests


def get_api_key():
    return os.getenv("GOOGLE_API_KEY") or os.getenv("Gemini_API_KEY") or ""


def get_model():
    return os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")


def test_gemini_api_key_connectivity():
    api_key = get_api_key()
    if not api_key:
        pytest.skip("No Google / Gemini API key found in active environment credentials.")

    model = get_model()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

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
        assert response.status_code == 200, (
            f"Expected HTTP 200 on free tier, got {response.status_code}: {response.text}"
        )
        
        reply = (
            response.json()
            .get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )
        print(f"\n💚 [Result] Gemini connectivity -> api_key_test.py -> POST /v1beta/models/{model}:generateContent -> returned HTTP {response.status_code} with reply: '{reply}'")

    except requests.exceptions.RequestException as exc:
        pytest.skip(f"Network error connecting to Gemini API: {exc}")


if __name__ == "__main__":
    test_gemini_api_key_connectivity()
