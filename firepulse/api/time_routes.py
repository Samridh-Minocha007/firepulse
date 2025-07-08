from fastapi import APIRouter, HTTPException, Request
from datetime import datetime
import httpx
import asyncio
import random
import pytz
from ..core.config import settings

router = APIRouter()

time_greetings = {
    "morning": [
        "☀️ Good Morning! Kickstart your day with these picks.",
        "🌞 Rise and shine! Movies to brighten your morning.",
        "☕ Grab your coffee! Here are some fresh movies to start your day.",
    ],
    "afternoon": [
        "🍿 Good afternoon! Enjoy these feel-good movies.",
        "🌤️ Afternoon delight: Check out these films.",
        "🕛 Taking a break? Here’s some entertainment for your afternoon.",
    ],
    "evening": [
        "🌆 Evening vibes? Here are some thrilling suggestions.",
        "🌇 Wind down your day with these exciting movies.",
        "🎬 The sun is setting, and the stage is set for these great films.",
    ],
    "night": [
        "🌙 Night owl? Dive into these mysteries and horrors.",
        "🦉 Late night thrills await you here.",
        "🌌 The night is dark and full of movies. Here are some to explore.",
    ],
    "late_night": [
        "🌌 Late night calm? Relax with these dramas and romances.",
        "🌠 Quiet night? These movies set the mood.",
        "🛋️ Cozy up on the couch with these soothing late-night stories.",
    ],
}

async def get_movies_async(client: httpx.AsyncClient, original_lang: str, page: int, genres: str = None, keywords: str = None):
    url = "https://api.themoviedb.org/3/discover/movie"
    params = {
        "api_key": settings.TMDB_API_KEY,
        "language": "en-US",
        "with_original_language": original_lang,
        "sort_by": "popularity.desc",
        "page": page,
        "include_adult": False,
        "vote_count.gte": 100
    }
    if genres:
        params["with_genres"] = genres
    elif keywords:
        params["with_keywords"] = keywords
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return {"type": original_lang, "data": response.json().get("results", [])}
    except Exception as e:
        print(f"Error fetching themed movies: {e}")
        return {"type": original_lang, "data": []}

async def get_latest_movies_async(client: httpx.AsyncClient):
    url = "https://api.themoviedb.org/3/movie/now_playing"
    params = {"api_key": settings.TMDB_API_KEY, "language": "en-US", "page": 1, "region": "IN"}
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return {"type": "latest", "data": response.json().get("results", [])}
    except Exception as e:
        print(f"Error fetching latest movies: {e}")
        return {"type": "latest", "data": []}

@router.get("/time-based-suggestions")
async def time_based_suggestions(request: Request, user_timezone: str = "Asia/Kolkata"):
    client: httpx.AsyncClient = request.app.state.httpx_client
    if not settings.TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="TMDB_API_KEY not configured.")

    try:
        tz = pytz.timezone(user_timezone)
        current_hour = datetime.now(tz).hour
    except pytz.UnknownTimeZoneError:
        user_timezone = "Asia/Kolkata"
        current_hour = datetime.now(pytz.timezone(user_timezone)).hour

    time_theme_map = {
        "morning": {"hours": range(5, 11), "genres": "35|18", "keywords": "9749|1804"},
        "afternoon": {"hours": range(11, 16), "genres": "10751|35", "keywords": "818|9749"},
        "evening": {"hours": range(16, 20), "genres": "28|53|80", "keywords": "9799|4344"},
        "night": {"hours": list(range(20, 24)) + list(range(0, 2)), "genres": "27|9648", "keywords": "10402|9663"},
        "late_night": {"hours": range(2, 5), "genres": "18|10749", "keywords": "225091|534"},
    }

    greeting = "Here are some great picks for you!"
    tasks = []
    
    for slot, info in time_theme_map.items():
        if current_hour in info["hours"]:
            greeting = random.choice(time_greetings.get(slot, [greeting]))
            random_page = random.randint(1, 5)
            for lang in ["en", "hi"]:
                tasks.append(get_movies_async(client, lang, random_page, genres=info["genres"]))
                tasks.append(get_movies_async(client, lang, random_page, keywords=info["keywords"]))
            tasks.append(get_latest_movies_async(client))
            break
    
    if not tasks:
        tasks.append(get_latest_movies_async(client))

    all_results = await asyncio.gather(*tasks)
    
    all_suggestions = [movie for result in all_results if result.get("data") for movie in result["data"]]
    latest_movies = [m for r in all_results if r.get("type") == "latest" for m in r.get("data", [])]
    unique_suggestions = list({movie['id']: movie for movie in all_suggestions}.values())
    latest_ids = {m['id'] for m in latest_movies}
    
    hindi_pool = [m for m in unique_suggestions if m.get("original_language") == "hi"]
    english_pool = [m for m in unique_suggestions if m.get("original_language") == "en"]
    latest_pool = [m for m in unique_suggestions if m.get("id") in latest_ids]
    
    final_suggestions = []
    seen_ids = set()

    random.shuffle(latest_pool)
    for movie in latest_pool:
        if len(final_suggestions) < 3 and movie['id'] not in seen_ids:
            final_suggestions.append(movie)
            seen_ids.add(movie['id'])
    
    random.shuffle(hindi_pool)
    for movie in hindi_pool:
        if len(final_suggestions) < 9 and movie['id'] not in seen_ids:
            final_suggestions.append(movie)
            seen_ids.add(movie['id'])
    
    random.shuffle(english_pool)
    for movie in english_pool:
        if len(final_suggestions) < 15 and movie['id'] not in seen_ids:
            final_suggestions.append(movie)
            seen_ids.add(movie['id'])
    
    random.shuffle(final_suggestions)

    formatted_suggestions = [
        {
            "title": movie.get("title"), "overview": movie.get("overview"), "release_date": movie.get("release_date"),
            "language": movie.get("original_language"), "vote_average": movie.get("vote_average"),
            "poster_path": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else None
        }
        for movie in final_suggestions
    ]

    return {
        "timezone_used": user_timezone, "current_hour_in_timezone": current_hour,
        "greeting": greeting, "suggestions": formatted_suggestions
    }