import os
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env.dev")
API_KEY = os.getenv("Gemini_API_KEY", "")
if not API_KEY: raise ValueError("No API key present")

url = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.5-flash:generateContent"
)

try:
    response = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        },
        json={
            "contents": [{
                "parts": [{
                    "text": "Reply with: Gemini is working!"
                }]
            }]
        },
        timeout=(15, 120)
    )

    print("HTTP Status:", response.status_code)
    print("Response:", response.json())

except requests.exceptions.RequestException as error:
    print("Request failed:", error)
