import httpx
import asyncio
import random
from typing import List, Optional
from transformers import pipeline
from ..core.config import TMDB_API_KEY

# --- Load the NLP model for emotion detection (for complex queries) ---
print("Loading NLP model for mood detection...")
try:
    emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)
    print("✅ NLP model loaded successfully.")
except Exception as e:
    print(f"❌ FAILED to load NLP model: {e}")
    emotion_classifier = None

# --- NEW: A dictionary for direct genre keyword matching ---
# This will be checked FIRST for accuracy and speed.
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
    1. First, it checks for direct genre keywords.
    2. If none are found, it uses the NLP model to detect underlying emotion.
    """
    text_lower = text.lower()
    
    # --- Step 1: Check for direct genre keywords first ---
    for genre, keywords in GENRE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                print(f"Direct keyword match found for genre: '{genre}'")
                return genre

    # --- Step 2: If no keyword match, use the NLP model ---
    if not emotion_classifier:
        print("NLP model is not available. Cannot extract mood.")
        return None
        
    try:
        print("No direct keywords found. Using NLP model for emotion detection...")
        results = emotion_classifier(text)
        if results and results[0]:
            detected_emotion = results[0][0]['label']
            print(f"NLP model detected emotion: '{detected_emotion}' from text: '{text}'")
            
            # Map the NLP model's output to our genres
            mood_map = {
                "joy": "comedy",
                "sadness": "drama",
                "anger": "action",
                "fear": "horror",
                "surprise": "thriller",
                "disgust": "horror"
            }
            mapped_mood = mood_map.get(detected_emotion)
            if mapped_mood:
                return mapped_mood
            # If the detected emotion is 'neutral', we can't recommend anything specific
            if detected_emotion == "neutral":
                return None
            return detected_emotion # Fallback for unmapped emotions like 'love'
        return None
    except Exception as e:
        print(f"Error during NLP mood extraction: {e}")
        return None


async def get_movies_by_mood(client: httpx.AsyncClient, mood: str) -> List[str]:
    """Gets a mixed list of English and Hindi movies concurrently based on mood/genre."""
    mood_to_genres = {
        "action": 28, "comedy": 35, "drama": 18, "romance": 10749,
        "horror": 27, "thriller": 53
    }
    
    genre_id = mood_to_genres.get(mood.lower())

    if not genre_id:
        return [f"Sorry, I don't have a genre category for '{mood}'."]

    # Helper function to fetch movies for a specific language
    async def fetch_movies_by_lang(lang: str):
        discover_url = "https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": TMDB_API_KEY, "with_genres": genre_id,
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

    # Create tasks to fetch English and Hindi movies at the same time
    tasks = [fetch_movies_by_lang("en"), fetch_movies_by_lang("hi")]
    results = await asyncio.gather(*tasks)
    
    combined = results[0] + results[1] # english_movies + hindi_movies
    if not combined:
        return ["Sorry, I couldn't find any movie suggestions for that right now."]

    random.shuffle(combined)
    return [movie.get("title", "Untitled") for movie in combined[:5]]

# --- The functions for actor/director search remain the same ---
async def search_person_async(client: httpx.AsyncClient, person_name: str) -> Optional[int]:
    url = "https://api.themoviedb.org/3/search/person"
    params = {"api_key": TMDB_API_KEY, "query": person_name}
    try:
        res = await client.get(url, params=params)
        res.raise_for_status()
        results = res.json().get("results", [])
        return results[0].get("id") if results else None
    except Exception as e:
        print(f"Error searching for person '{person_name}': {e}")
        return None

async def get_movies_by_person_async(client: httpx.AsyncClient, person_id: int) -> List[str]:
    url = f"https://api.themoviedb.org/3/discover/movie"
    params = {"api_key": TMDB_API_KEY, "with_people": person_id, "sort_by": "popularity.desc"}
    try:
        res = await client.get(url, params=params)
        res.raise_for_status()
        movies_data = res.json().get("results", [])[:5]
        return [movie.get("title", "Untitled") for movie in movies_data]
    except Exception as e:
        print(f"Error fetching movies for person ID {person_id}: {e}")
        return []

