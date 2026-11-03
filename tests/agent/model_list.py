import os
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env.dsev")
API_KEY = os.getenv("Gemini_API_KEY", "")
if not API_KEY: raise ValueError("No API key present")

url = "https://generativelanguage.googleapis.com/v1beta/models"

try:
    response = requests.get(
        url,
        headers={"x-goog-api-key": API_KEY},
        params={"pageSize": 5},
        timeout=(10, 30)
    )

    print("HTTP Status:", response.status_code)
    print("Response:", response.json())

except requests.exceptions.ConnectTimeout:
    print("Connection timeout: Could not connect to Google.")

except requests.exceptions.ReadTimeout:
    print("Read timeout: Google did not respond in time.")

except requests.exceptions.RequestException as error:
    print("Network error:", error)
