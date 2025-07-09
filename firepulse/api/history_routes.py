from fastapi import APIRouter, HTTPException, Body, Request, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
import re
from thefuzz import fuzz
from sqlalchemy.orm import Session
import random
import asyncio

from ..core.config import settings
from ..core.db import SessionLocal
from ..api.auth_routes import get_current_user
from ..models.user import User as UserModel
from ..crud import history as history_crud

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class WatchedMovie(BaseModel):
    movie_name: str


def normalize(text: str) -> str:
    return re.sub(r"[^\w\s]", "", text.lower()).strip()

async def search_for_movie_id(client: httpx.AsyncClient, movie_name: str) -> int:
    """Searches for a movie and returns its ID. Raises HTTPException on failure."""
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": settings.TMDB_API_KEY, "query": movie_name}

    for attempt in range(3):
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            if not results:
                raise HTTPException(status_code=404, detail=f"No results found for '{movie_name}'.")

            best_match = max(results, key=lambda m: fuzz.ratio(normalize(movie_name), normalize(m.get("title", ""))))

            if fuzz.ratio(normalize(movie_name), normalize(best_match.get("title", ""))) >= 85:
                return best_match["id"]
            else:
                raise HTTPException(status_code=404, detail=f"Could not find a confident match for '{movie_name}'.")
        except httpx.ConnectError as e:
            print(f"Attempt {attempt + 1} failed for search_for_movie_id: {e}")
            await asyncio.sleep(1)

    raise HTTPException(status_code=504, detail="Could not connect to movie search service.")


async def get_movie_details(client: httpx.AsyncClient, movie_id: int) -> Dict[str, Any]:
    """Fetches movie details. Raises HTTPException on failure or if genres are missing."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": settings.TMDB_API_KEY}

    for attempt in range(3):
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            movie_data = response.json()

            
            if not movie_data.get("genres"):
                raise ValueError(f"Movie details response for ID {movie_id} is missing 'genres' field or it is empty.")

            return {
                "id": movie_data.get("id"),
                "title": movie_data.get("title"),
                "genres": [genre['id'] for genre in movie_data.get("genres", [])]
            }
        except (httpx.ConnectError, ValueError) as e:
            print(f"Attempt {attempt + 1} failed for get_movie_details: {e}")
            await asyncio.sleep(1)

    raise HTTPException(status_code=504, detail="Could not fetch valid details from the movie service.")



@router.post("/history/log-watch", tags=["User History & Recommendations"])
async def log_watch_history(
    watched_movie: WatchedMovie, 
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Logs a movie to the current authenticated user's watch history."""
    client: httpx.AsyncClient = request.app.state.httpx_client

    try:
        movie_id = await search_for_movie_id(client, watched_movie.movie_name)
        movie_details = await get_movie_details(client, movie_id)

        history_crud.add_movie_to_history(db=db, user_id=current_user.id, movie_details=movie_details)

        return {"message": f"Successfully logged '{movie_details['title']}' to your watch history."}
    except HTTPException as e:
        
        raise e

@router.get("/history/recommendations", tags=["User History & Recommendations"])
async def get_history_based_recommendations(
    request: Request,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Gets movie recommendations based on the current user's watch history."""
    client: httpx.AsyncClient = request.app.state.httpx_client

    user_history = history_crud.get_user_movie_history(db, user_id=current_user.id)
    if not user_history:
        raise HTTPException(status_code=404, detail="No watch history found. Log some movies first!")

    last_watched_movie = user_history[0]
    genre_ids = last_watched_movie.genres
    if not genre_ids:
        raise HTTPException(status_code=404, detail="Last watched movie has no genre information.")

    genre_id_string = "|".join(map(str, genre_ids))
    recommendations_url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "with_genres": genre_id_string,
        "sort_by": "popularity.desc",
        "page": random.randint(1, 5)
    }

    for attempt in range(3):
        try:
            response = await client.get(recommendations_url, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])

            watched_ids = {h.tmdb_id for h in user_history}
            suggestions = [movie for movie in results if movie.get("id") not in watched_ids]

            return {
                "recommending_based_on": f"your last watched movie: '{last_watched_movie.movie_title}'",
                "suggestions": suggestions[:10]
            }
        except httpx.ConnectError as e:
            print(f"Attempt {attempt + 1} failed: Connection error. Retrying...")
            await asyncio.sleep(1)

    raise HTTPException(status_code=504, detail="Could not connect to the movie service after multiple attempts.")