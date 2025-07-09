# firepulse/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import List, Optional
from .trivia import Badge # Ensure this import is correct

# --- User Schemas ---

# Shared properties
class UserBase(BaseModel):
    email: EmailStr

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to return to client (Full User details, consolidated definition)
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    google_creds_json: Optional[str] = None # Added for Google OAuth credentials
    total_points: int = 0 # Added for trivia game points
    badges: List[Badge] = [] # Added for user badges

    # This is the modern way to configure the model for Pydantic v2+
    model_config = ConfigDict(from_attributes=True)

# Schema for the JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str
