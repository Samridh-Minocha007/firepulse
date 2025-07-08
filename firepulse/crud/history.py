# firepulse/crud/history.py
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..models.history import MovieHistory 

def get_user_movie_history(db: Session, user_id: int):
    """Fetches the movie watch history for a specific user."""
    return db.query(MovieHistory).filter(MovieHistory.user_id == user_id).order_by(MovieHistory.watched_at.desc()).all()

def add_movie_to_history(db: Session, user_id: int, movie_details: dict):
    """
    Adds a new movie to a user's watch history.
    If the movie already exists, it updates the watched_at timestamp.
    """
    existing_entry = db.query(MovieHistory).filter_by(user_id=user_id, tmdb_id=movie_details['id']).first()

    if existing_entry:
        # --- THIS IS THE FIX for the timestamp bug ---
        existing_entry.watched_at = func.now()
        db.commit()
        db.refresh(existing_entry)
        return existing_entry

    # If it's a new entry, create it
    db_history_item = MovieHistory(
        user_id=user_id, 
        movie_title=movie_details['title'],
        tmdb_id=movie_details['id'],
        genres=movie_details['genres']
    )
    db.add(db_history_item)
    db.commit()
    db.refresh(db_history_item)
    return db_history_item
