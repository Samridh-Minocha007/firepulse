from sqlalchemy.orm import Session
import random
import asyncio # <-- NEW IMPORT
from ..crud import history as history_crud
from ..crud import user as user_crud
from ..services import movie_bot

async def suggest_movie_for_group(db: Session, client, user_emails: list[str]):
    
    all_history_items = []
    watched_movie_ids = set()

    for email in user_emails:
        user = user_crud.get_user_by_email(db, email=email)
        if user:
            user_history = history_crud.get_user_movie_history(db, user_id=user.id)
            all_history_items.extend(user_history)
            for item in user_history:
                watched_movie_ids.add(item.tmdb_id)

    if not all_history_items:
        movies = await movie_bot.get_movies_by_mood(client, "comedy")
        return random.choice(movies) if movies else "No suggestion found."

    
    recommendation_tasks = []
    for item in all_history_items:
        recommendation_tasks.append(
            movie_bot.get_recommendations_for_movie(client, item.tmdb_id)
        )

    
    print(f"DEBUG: Fetching recommendations for {len(recommendation_tasks)} seed movies...")
    list_of_recommendation_lists = await asyncio.gather(*recommendation_tasks)

    
    potential_suggestions = []
    for rec_list in list_of_recommendation_lists:
        potential_suggestions.extend(rec_list)

    if not potential_suggestions:
        return "Could not find any recommendations based on your group's history."

    
    seen_suggestion_ids = set()
    new_suggestions = []
    for movie in potential_suggestions:
        movie_id = movie.get("id")
        if movie_id and movie_id not in watched_movie_ids and movie_id not in seen_suggestion_ids:
            new_suggestions.append(movie)
            seen_suggestion_ids.add(movie_id)

    if not new_suggestions:
        return "Found some recommendations, but you've seen them all! Try logging more movies."

   
    return random.choice(new_suggestions).get("title", "No suggestion found.")