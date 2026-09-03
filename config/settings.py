import os
from dotenv import load_dotenv

class Settings:
    def __init__(self):
        load_dotenv()

    def load_api_key(self):
        key = os.getenv("GEMINI_API_KEY")
        if not key:
            raise ValueError("Gemini API Key missing")
        return key
