# firepulse/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings

# Create the SQLAlchemy engine.
# FIX: Convert the Pydantic PostgresDsn object back to a string,
# which is the format create_engine expects.
engine = create_engine(
    str(settings.DATABASE_URL)
)

# Create a SessionLocal class
# Each instance of a SessionLocal will be a new database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class
# Our ORM models will inherit from this class
Base = declarative_base()
