from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.db import Base
from .user import User

class MovieHistory(Base):
    __tablename__ = "movie_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_title = Column(String, nullable=False)
   
    tmdb_id = Column(Integer, nullable=False)
    genres = Column(JSONB)

    watched_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")