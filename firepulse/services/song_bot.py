import httpx
import random  
from typing import List, Optional
from fastapi import Request
from ..services import spotify_helper
import random

SONG_MOOD_KEYWORDS = {
    "happy": ["happy", "joy", "dance", "party", "energetic", "fun"],
    "sad": ["sad", "cry", "heartbreak", "pain", "lonely", "melancholy"],
    "romantic": ["romance", "love", "crush", "valentine", "affection", "date"],
    "angry": ["angry", "rage", "mad", "frustrated"],
    "relax": ["calm", "chill", "relax", "soothing", "peaceful", "lofi"],
    "motivational": ["motivate", "success", "power", "goal", "win", "strong"],
    "spiritual": ["devotional", "bhajan", "mantra", "spiritual", "god"]
}

def extract_song_mood(text: str) -> Optional[str]:
    """Extracts the most likely song mood from a text string based on keywords."""
    text = text.lower()
    scores = {mood: 0 for mood in SONG_MOOD_KEYWORDS}
    for mood, keywords in SONG_MOOD_KEYWORDS.items():
        for word in keywords:
            if word in text:
                scores[mood] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None

async def get_songs_by_mood(request: Request, mood: str, language_hint: Optional[str] = None, limit: int = 10) -> List[str]:
    """Asynchronously gets song recommendations from Spotify based on mood."""
    client: httpx.AsyncClient = request.app.state.httpx_client
    token = await spotify_helper.get_spotify_token(request)
    if not token:
        return ["Failed to authenticate with Spotify."]

    query = mood
    if language_hint:
        query += f" {language_hint}"

    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": limit}
    url = "https://api.spotify.com/v1/search"

    try:
        res = await client.get(url, headers=headers, params=params)
        res.raise_for_status()
        
        songs = []
        for item in res.json().get("tracks", {}).get("items", []):
            name = item.get("name", "Untitled")
            artist = item.get("artists", [{}])[0].get("name", "Unknown Artist")
            songs.append(f"{name} by {artist}")
        
        if songs:
            random.shuffle(songs) 
            return songs[:5] 
            
        return ["No songs found for that mood."]
        
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"Error fetching songs by mood from Spotify: {e}")
        return ["Failed to fetch songs from Spotify."]


async def get_songs_by_artist(request: Request, artist_name: str, limit: int = 10) -> List[str]:
    """Asynchronously gets songs by a specific artist from Spotify."""
    client: httpx.AsyncClient = request.app.state.httpx_client
    token = await spotify_helper.get_spotify_token(request)
    if not token:
        return ["Failed to authenticate with Spotify."]

    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": f"artist:{artist_name}", "type": "track", "limit": limit}
    url = "https://api.spotify.com/v1/search"

    try:
        res = await client.get(url, headers=headers, params=params)
        res.raise_for_status()

        songs = []
        for item in res.json().get("tracks", {}).get("items", []):
            name = item.get("name", "Untitled")
            artist = item.get("artists", [{}])[0].get("name", "Unknown Artist")
            songs.append(f"{name} by {artist}")

        if songs:
            
            random.shuffle(songs)
            return songs[:5] 

        return [] 

    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"Error fetching songs by artist from Spotify: {e}")
        return ["Failed to fetch songs from Spotify."]