import httpx
from gtts import gTTS
import uuid
import os
import asyncio
from typing import Optional

# --- Directory setup for static audio files ---
# This ensures the directory for saving audio files exists when the module is loaded.
STATIC_DIR = "app/static"
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)


# --- FIX: The function signature is now async and correctly accepts both 'client' and 'text' ---
async def text_to_speech(client: httpx.AsyncClient, text: str) -> Optional[str]:
    """
    Asynchronously generates speech from text using gTTS and saves it to a static file.
    It runs the blocking gTTS save operation in a separate thread to avoid blocking the main server loop.
    
    Args:
        client: The shared httpx.AsyncClient (for pattern consistency).
        text: The text to be converted to speech.

    Returns:
        The URL path to the generated MP3 file, or None on failure.
    """
    if not text:
        return None
        
    try:
        # Create a unique filename for each audio clip to prevent overwriting.
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        # Initialize the gTTS object with the text to be converted.
        tts = gTTS(text, lang='en')
        
        # Run the synchronous (blocking) tts.save() function in a background thread.
        # This is the correct way to handle blocking I/O in an async application.
        await asyncio.to_thread(tts.save, filepath)

        # Return the web-accessible path to the saved audio file.
        return f"/static/audio/{filename}"

    except Exception as e:
        # Print any error that occurs during the process and return None.
        print(f"Error generating text-to-speech audio: {e}")
        return None
