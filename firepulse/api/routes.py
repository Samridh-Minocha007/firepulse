from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import httpx


from ..services import movie_bot, song_bot, voice

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/movies")
async def get_movie_suggestions(query_request: QueryRequest, request: Request):
    """
    Handles ONLY movie recommendation requests.
    It first tries to find a person (actor/director) and falls back to a movie mood.
    """
    client: httpx.AsyncClient = request.app.state.httpx_client
    query_text = query_request.query.strip()
    
   
    person_name = query_text.title()
    person_id = await movie_bot.search_person_async(client, person_name)
    
    
    if person_id:
        movie_results = await movie_bot.get_movies_by_person_async(client, person_id)
        if not movie_results:
            message = f"I found {person_name}, but couldn't fetch their popular movies right now."
        else:
            message = f"Here are some popular movies with {person_name}: {', '.join(movie_results)}"
        
        voice_url: str | None = await voice.text_to_speech(client, message)
        return {"text": message, "voice_url": voice_url}

    
    movie_mood = movie_bot.extract_mood(query_text)
    if not movie_mood:
        raise HTTPException(status_code=404, detail="Sorry, I couldn't find an actor/director by that name or understand the mood.")
    
    movies: list[str] = await movie_bot.get_movies_by_mood(client, movie_mood) 
    
    message = f"Here are some {movie_mood}-based movie recommendations: {', '.join(movies)}"
    
    voice_url: str | None = await voice.text_to_speech(client, message)
    return {"text": message, "voice_url": voice_url}


@router.post("/songs")
async def get_song_suggestions(query_request: QueryRequest, request: Request):
    """
    Handles ONLY song recommendation requests.
    It first tries to find an artist and falls back to a song mood.
    """
    query_text = query_request.query.strip()
    artist_name = query_text.title()

   
    song_results: list[str] = await song_bot.get_songs_by_artist(request, artist_name)
    
    if song_results and "Failed" not in song_results[0]:
       
        print("\n--- DEBUG MARKER: CONSTRUCTING SONG MESSAGE ---")
        message = f"Here are some songs by {artist_name}: " + ", ".join(song_results)
        print(f"--- DEBUG MARKER: FINAL MESSAGE BEING SENT: '{message}' ---\n")
        

        voice_url: str | None = await voice.text_to_speech(request.app.state.httpx_client, message)
        return {"text": message, "voice_url": voice_url}
    
    
    song_mood = song_bot.extract_song_mood(query_text)
    if not song_mood:
        raise HTTPException(
            status_code=404,
            detail="Sorry, I couldn't find that artist or understand the mood."
        )
    
    language_hint = "hindi" if "hindi" in query_text.lower() else None
    mood_songs: list[str] = await song_bot.get_songs_by_mood(request, song_mood, language_hint)
    
    if mood_songs and "Failed" in mood_songs[0]:
        raise HTTPException(status_code=500, detail=mood_songs[0])

    message = f"Here are some {song_mood}-based song recommendations: " + ", ".join(mood_songs)
    
    voice_url: str | None = await voice.text_to_speech(request.app.state.httpx_client, message)
    return {"text": message, "voice_url": voice_url}
