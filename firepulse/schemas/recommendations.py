from pydantic import BaseModel
from typing import Optional

class MovieRecommendationRequest(BaseModel):
    genre: str
    language: Optional[str] = None

class SongRecommendationRequest(BaseModel):
    artist: str
    language: Optional[str] = None