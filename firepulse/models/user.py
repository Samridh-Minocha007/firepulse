from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.db import Base 


from .trivia import user_badge_association

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    google_creds_json = Column(Text, nullable=True)
    total_points = Column(Integer, default=0) 
    
    badges = relationship(
        "Badge",
        secondary=user_badge_association,
        backref="users"
    )
