from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import re
import httpx

# Import your service functions
from ..services import movie_bot, song_bot, voice

# This is the crucial line: define the router object that main.py will import.
router = APIRouter()

class AskRequest(BaseModel):
    query: str

@router.post("/ask")
async def ask_bot(ask_request: AskRequest, request: Request):
    """
    Handles movie recommendation requests for moods, actors, or directors.
    """
    client: httpx.AsyncClient = request.app.state.httpx_client
    query_text = ask_request.query.lower()
    
    # --- FIX: The regular expression is now more flexible ---
    # It now recognizes phrases like "movies of", "films by", "directed by", etc.
    person_match = re.search(r"(?:movies by|movies with|starring|movies of|films by|directed by)\s+(.+)", query_text)
    if person_match:
        person_name = person_match.group(1).strip()
        person_id = await movie_bot.search_person_async(client, person_name)
        
        if not person_id:
            raise HTTPException(status_code=404, detail=f"Sorry, I couldn't find an actor or director named '{person_name}'.")
        
        movies = await movie_bot.get_movies_by_person_async(client, person_id)
        if not movies:
            message = f"I found {person_name}, but couldn't fetch their popular movies right now."
        else:
            message = f"Here are some popular movies with {person_name}: {', '.join(movies)}"
        
        voice_url: str | None = await voice.text_to_speech(client, message)
        return {"text": message, "voice_url": voice_url}

    # Fallback to mood-based search if no person is found
    mood = movie_bot.extract_mood(query_text)
    if not mood:
        raise HTTPException(status_code=400, detail="Sorry, I couldn't understand a mood, actor, or director in your request.")
    
    movies: list[str] = await movie_bot.get_movies_by_mood(client, mood) 
    
    message = f"Here are some {mood}-based movie recommendations: {', '.join(movies)}"
    
    voice_url: str | None = await voice.text_to_speech(client, message)
    return {"text": message, "voice_url": voice_url}


@router.post("/songs")
async def suggest_songs(ask_request: AskRequest, request: Request):
    """Handles song recommendation requests based on mood or artist."""
    query_text = ask_request.query.lower()
    
    # Handle requests for a specific artist
    artist_match = re.search(r"(?:songs by|play|songs from|listen to)\s+(.+)", query_text)
    if artist_match:
        artist_name = artist_match.group(1).strip()
        songs: list[str] = await song_bot.get_songs_by_artist(request, artist_name)
        if songs and "Failed" in songs[0]:
            raise HTTPException(status_code=500, detail=songs[0])
        message = f"Here are some songs by {artist_name}: " + ", ".join(songs)
        return {"text": message, "voice_url": None}
    
    # Handle requests based on mood
    mood = song_bot.extract_song_mood(query_text)
    if not mood:
        raise HTTPException(
            status_code=400,
            detail="Sorry, I couldn't figure out the mood. Try something like 'play sad songs' or 'romantic Hindi music'."
        )
    
    language_hint = "hindi" if "hindi" in query_text else None
    songs: list[str] = await song_bot.get_songs_by_mood(request, mood, language_hint)
    if songs and "Failed" in songs[0]:
        raise HTTPException(status_code=500, detail=songs[0])

    message = f"Here are some {mood}-based song recommendations: " + ", ".join(songs)
    
    client: httpx.AsyncClient = request.app.state.httpx_client
    voice_url: str | None = await voice.text_to_speech(client, message)
    
    return {"text": message, "voice_url": voice_url}
