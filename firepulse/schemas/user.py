# firepulse/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import List
from .trivia import Badge

# --- User Schemas ---

# Shared properties
class UserBase(BaseModel):
    email: EmailStr

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to return to client
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    # This is the modern way to configure the model for Pydantic v2+
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    badges: List[Badge] = [] # <-- NEW FIELD

    model_config = ConfigDict(from_attributes=True)