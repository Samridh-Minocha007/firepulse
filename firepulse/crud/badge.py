# firepulse/crud/badge.py
from sqlalchemy.orm import Session
from ..models.trivia import Badge

def get_badge_by_name(db: Session, name: str):
    """Fetches a badge by its name."""
    return db.query(Badge).filter(Badge.name == name).first()

def create_badge(db: Session, name: str, description: str):
    """Creates a new badge if it doesn't already exist."""
    db_badge = get_badge_by_name(db, name=name)
    if not db_badge:
        db_badge = Badge(name=name, description=description)
        db.add(db_badge)
        db.commit()
        db.refresh(db_badge)
    return db_badge
