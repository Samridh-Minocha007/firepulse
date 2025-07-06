from fastapi import APIRouter, HTTPException, Body, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import os
import random
import re
from thefuzz import fuzz

router = APIRouter()

# Import the API key from your central config file
from ..core.config import TMDB_API_KEY

# In-Memory "Database" for Watch History (for prototyping)
user_watch_histories: Dict[str, List[Dict[str, Any]]] = {}

# Pydantic Model for the Request Body
class WatchedMovie(BaseModel):
    movie_name: str


# --- Helper Functions ---

def normalize(text: str) -> str:
    """Removes punctuation and lowercases the input string."""
    return re.sub(r"[^\w\s]", "", text.lower()).strip()

async def search_for_movie_id(client: httpx.AsyncClient, movie_name: str) -> Optional[int]:
    """
    Searches for a movie on TMDB using fuzzy logic and returns the best-matched ID.
    Includes fallback to exact match and handles TMDB errors gracefully.
    """
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": movie_name, "language": "en-US", "page": 1}

    if not TMDB_API_KEY:
        print("❌ CRITICAL: TMDB_API_KEY is missing.")
        return None

    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("results", [])

        if not results:
            return None

        best_match = None
        best_score = 0
        normalized_input = normalize(movie_name)

        for movie in results[:20]:
            title = movie.get("title", "")
            score = fuzz.partial_ratio(normalized_input, normalize(title))
            popularity_bonus = movie.get("popularity", 0) / 1000
            total_score = score + popularity_bonus

            if total_score > best_score:
                best_score = total_score
                best_match = movie

        # Debug log top 3 fuzzy matches
        top_matches = sorted(
            results[:20],
            key=lambda m: fuzz.partial_ratio(normalized_input, normalize(m.get("title", ""))),
            reverse=True
        )[:3]
        print(f"Top fuzzy matches for '{movie_name}':")
        for m in top_matches:
            t = m.get("title", "")
            s = fuzz.partial_ratio(normalized_input, normalize(t))
            print(f"  - {t} (score: {s})")

        if best_match:
            print(f"🎯 Best match for '{movie_name}': {best_match.get('title')} (score={best_score})")

        if best_score >= 85:
            return best_match.get("id")

        # Fallback to exact match (case-insensitive)
        for movie in results:
            if movie.get("title", "").lower() == movie_name.lower():
                return movie.get("id")

        return None

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            print(f"🕒 TMDB rate limit exceeded for '{movie_name}'.")
        else:
            print(f"❌ TMDB returned HTTP error {e.response.status_code} for '{movie_name}': {e.response.text}")
        return None
    except Exception as e:
        print(f"❌ Error during TMDB movie search for '{movie_name}': {e}")
        return None


async def get_movie_details(client: httpx.AsyncClient, movie_id: int) -> Dict[str, Any]:
    """Fetches details for a specific movie ID from TMDB."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        movie_data = response.json()
        return {
            "id": movie_data.get("id"),
            "title": movie_data.get("title"),
            "genres": [genre['id'] for genre in movie_data.get("genres", [])]
        }
    except Exception as e:
        print(f"Error fetching movie details for ID {movie_id}: {e}")
        return {}


# --- API Endpoints ---

@router.post("/history/log-watch/{user_id}")
async def log_watch_history(user_id: str, watched_movie: WatchedMovie, request: Request):
    client: httpx.AsyncClient = request.app.state.httpx_client
    movie_name = watched_movie.movie_name
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="TMDB_API_KEY not configured.")
    
    movie_id = await search_for_movie_id(client, movie_name)
    if not movie_id:
        raise HTTPException(status_code=404, detail=f"Could not find a confident match for a movie named '{movie_name}'. Please try a more specific title.")
    
    movie_details = await get_movie_details(client, movie_id)
    if not movie_details:
        raise HTTPException(status_code=404, detail=f"Found a match for '{movie_name}' but could not fetch its details.")

    if user_id not in user_watch_histories:
        user_watch_histories[user_id] = []

    # Avoid duplicates by movie ID
    user_watch_histories[user_id] = [m for m in user_watch_histories[user_id] if m['id'] != movie_id]
    user_watch_histories[user_id].append(movie_details)

    return {
        "message": f"Successfully logged '{movie_details['title']}' to {user_id}'s watch history.",
        "current_history": user_watch_histories[user_id]
    }


@router.get("/history/recommendations/{user_id}")
async def get_history_based_recommendations(user_id: str, request: Request):
    client: httpx.AsyncClient = request.app.state.httpx_client
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="TMDB_API_KEY not configured.")

    if user_id not in user_watch_histories or not user_watch_histories[user_id]:
        raise HTTPException(status_code=404, detail=f"No watch history found for user '{user_id}'.")

    last_watched_movie = user_watch_histories[user_id][-1]
    last_watched_title = last_watched_movie["title"]
    genre_ids = last_watched_movie.get("genres", [])
    if not genre_ids:
        raise HTTPException(status_code=404, detail=f"Last watched movie has no genre information.")

    genre_id_string = "|".join(map(str, genre_ids))
    recommendations_url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": genre_id_string,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "page": random.randint(1, 5),
        "include_adult": False,
        "vote_count.gte": 100
    }

    response = await client.get(recommendations_url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch recommendations from TMDB.")

    results = response.json().get("results", [])
    suggestions = [movie for movie in results if movie.get("id") != last_watched_movie["id"]]
    
    formatted_suggestions = [
        {
            "title": movie.get("title"),
            "overview": movie.get("overview"),
            "poster_path": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else None
        }
        for movie in suggestions[:15]
    ]

    return {
        "recommending_based_on": f"your last watched movie: '{last_watched_title}'",
        "suggestions": formatted_suggestions
    }
