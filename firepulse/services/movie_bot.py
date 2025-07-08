import httpx
import asyncio
import random
from typing import List, Optional ,Dict,Any
from transformers import pipeline
# --- MODIFIED: Import the settings object instead of individual keys ---
from ..core.config import settings

# --- Load the NLP model for emotion detection (for complex queries) ---
print("Loading NLP model for mood detection...")
try:
    emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)
    print("✅ NLP model loaded successfully.")
except Exception as e:
    print(f"❌ FAILED to load NLP model: {e}")
    emotion_classifier = None

# --- A dictionary for direct genre keyword matching ---
GENRE_KEYWORDS = {
    "action": ["action", "fight", "adventure", "stunt", "chase"],
    "comedy": ["comedy", "funny", "laugh", "hilarious", "jokes", "humor", "sitcom"],
    "drama": ["drama", "sad", "unhappy", "depressed", "melancholy", "cry", "serious", "emotional"],
    "romance": ["romance", "love", "crush", "valentine", "affection", "date", "relationship", "romantic"],
    "horror": ["horror", "fear", "scared", "frightened", "terror", "creepy", "spooky", "ghost", "monster"],
    "thriller": ["thriller", "thrill", "suspense", "intense", "mystery", "detective", "edge-of-your-seat"]
}

def extract_mood(text: str) -> Optional[str]:
    """
    Extracts mood or genre using a hybrid approach.
    """
    text_lower = text.lower()
    
    # Check for direct genre keywords first
    for genre, keywords in GENRE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                print(f"Direct keyword match found for genre: '{genre}'")
                return genre

    # If no keyword match, use the NLP model
    if not emotion_classifier:
        print("NLP model is not available. Cannot extract mood.")
        return None
        
    try:
        print("No direct keywords found. Using NLP model for emotion detection...")
        results = emotion_classifier(text)
        if results and results[0]:
            detected_emotion = results[0][0]['label']
            print(f"NLP model detected emotion: '{detected_emotion}' from text: '{text}'")
            
            mood_map = {
                "joy": "comedy", "sadness": "drama", "anger": "action",
                "fear": "horror", "surprise": "thriller", "disgust": "horror", "love": "romance"
            }
            mapped_mood = mood_map.get(detected_emotion)
            if mapped_mood:
                return mapped_mood
            if detected_emotion == "neutral":
                return None
            return detected_emotion
        return None
    except Exception as e:
        print(f"Error during NLP mood extraction: {e}")
        return None


async def get_movies_by_mood(client: httpx.AsyncClient, mood: str) -> List[str]:
    """Gets a randomized, mixed list of English and Hindi movies concurrently."""
    mood_to_genres = {
        "action": 28, "comedy": 35, "drama": 18, "romance": 10749,
        "horror": 27, "thriller": 53
    }
    
    genre_id = mood_to_genres.get(mood.lower())
    if not genre_id:
        return [f"Sorry, I don't have a genre category for '{mood}'."]

    async def fetch_movies_by_lang(lang: str):
        discover_url = "https://api.themoviedb.org/3/discover/movie"
        params = {
            # --- MODIFIED: Use settings object ---
            "api_key": settings.TMDB_API_KEY, "with_genres": genre_id,
            "with_original_language": lang, "language": "en-US",
            "sort_by": "popularity.desc", "page": random.randint(1, 5)
        }
        try:
            res = await client.get(discover_url, params=params)
            res.raise_for_status()
            return res.json().get("results", [])
        except Exception as e:
            print(f"Error fetching {lang} movies for genre {genre_id}: {e}")
            return []

    tasks = [fetch_movies_by_lang("en"), fetch_movies_by_lang("hi")]
    results = await asyncio.gather(*tasks)
    
    combined = results[0] + results[1]
    if not combined:
        return ["Sorry, I couldn't find any movie suggestions for that right now."]

    random.shuffle(combined)
    return [movie.get("title", "Untitled") for movie in combined[:5]]


async def search_person_async(client: httpx.AsyncClient, person_name: str) -> Optional[int]:
    """Searches for a person on TMDB and returns their ID."""
    url = "https://api.themoviedb.org/3/search/person"
    # --- MODIFIED: Use settings object ---
    params = {"api_key": settings.TMDB_API_KEY, "query": person_name}
    try:
        res = await client.get(url, params=params)
        res.raise_for_status()
        results = res.json().get("results", [])
        return results[0].get("id") if results else None
    except Exception as e:
        print(f"Error searching for person '{person_name}': {e}")
        return None

async def get_movies_by_person_async(client: httpx.AsyncClient, person_id: int) -> List[str]:
    """Gets a randomized list of popular movies for a given person ID."""
    url = f"https://api.themoviedb.org/3/discover/movie"
    # --- MODIFIED: Use settings object ---
    params = {"api_key": settings.TMDB_API_KEY, "with_people": person_id, "sort_by": "popularity.desc"}
    try:
        res = await client.get(url, params=params)
        res.raise_for_status()
        movies_data = res.json().get("results", [])
        
        random.shuffle(movies_data)
        
        return [movie.get("title", "Untitled") for movie in movies_data[:5]]
    except Exception as e:
        print(f"Error fetching movies for person ID {person_id}: {e}")
        return []
    
async def get_movies_by_genre_id(client: httpx.AsyncClient, genre_id: int) -> List[str]:
    """Gets a list of movies for a specific genre ID."""
    discover_url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "with_genres": genre_id,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": random.randint(1, 5)
    }
    try:
        res = await client.get(discover_url, params=params)
        res.raise_for_status()
        results = res.json().get("results", [])
        return [movie.get("title", "Untitled") for movie in results]
    except Exception as e:
        print(f"Error fetching movies for genre ID {genre_id}: {e}")
        return []

# --- THIS IS THE NEW FUNCTION THAT WAS MISSING ---
async def get_recommendations_for_movie(client: httpx.AsyncClient, movie_id: int) -> List[Dict[str, Any]]:
    """Gets a list of recommended movies for a specific movie ID with retry logic."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
    params = {"api_key": settings.TMDB_API_KEY, "language": "en-US", "page": 1}

    for attempt in range(3): # Try up to 3 times
        try:
            res = await client.get(url, params=params)
            res.raise_for_status()
            results = res.json().get("results", [])
            return results
        except (httpx.ConnectError, httpx.ReadTimeout) as e:
            print(f"Attempt {attempt + 1} failed for get_recommendations_for_movie (ID: {movie_id}): {e}")
            await asyncio.sleep(1) # Wait 1 second before retrying
        except Exception as e:
            print(f"An unexpected error occurred fetching recommendations for movie ID {movie_id}: {e}")
            return [] # Don't retry on other errors

    print(f"All attempts failed for get_recommendations_for_movie (ID: {movie_id})")
    return [] # Return empty list if all attempts fail
