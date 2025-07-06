import os
from dotenv import load_dotenv

# This loads your .env file from the project root
load_dotenv()

# --- Define all your application settings here ---
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# --- Verification Check ---
if not all([TMDB_API_KEY, GEMINI_API_KEY, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET]):
    print("❌ CRITICAL ERROR: One or more API keys are missing. Please check your .env file.")
else:
    print("✅ All API Keys successfully loaded from .env file.")