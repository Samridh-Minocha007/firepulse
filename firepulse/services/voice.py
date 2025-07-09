import httpx
from gtts import gTTS
import uuid
import os
import asyncio
from typing import Optional


STATIC_DIR = "app/static"
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)



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
        
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        
        tts = gTTS(text, lang='en')
        
        
        await asyncio.to_thread(tts.save, filepath)

        
        return f"/static/audio/{filename}"

    except Exception as e:
        
        print(f"Error generating text-to-speech audio: {e}")
        return None
