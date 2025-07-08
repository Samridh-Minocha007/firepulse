# firepulse/crud/user.py
from sqlalchemy.orm import Session
from ..models import user as user_model
from ..schemas import user as user_schema
from ..core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    """Fetches a user by their email address."""
    return db.query(user_model.User).filter(user_model.User.email == email).first()

def create_user(db: Session, user: user_schema.UserCreate):
    """Creates a new user in the database."""
    hashed_password = get_password_hash(user.password)
    db_user = user_model.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_google_creds(db: Session, user_email: str, creds_json: str):
    """Updates a user's Google credentials."""
    db_user = get_user_by_email(db, email=user_email)
    if db_user:
        db_user.google_creds_json = creds_json
        db.commit()
        db.refresh(db_user)
    return db_user
