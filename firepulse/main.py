from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import httpx
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings

# --- NEW: Import database components ---
from .core.db import Base, engine
from .models import user  # This import is crucial so Base knows about the User model

# --- Import all of your API routers ---
from .api.routes import router as general_router
from .api import time_routes
from .api import trivia_routes
from .api import history_routes
from .api import auth_routes
from .api import watch_party_routes

# Lifespan manager to create and manage resources
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will print when the application starts
    print("--- FirePulse+ API starting. HTTP client created. ---")
    app.state.httpx_client = httpx.AsyncClient(timeout=30.0)
    
    # --- NEW: Create database tables on startup ---
    print("Creating database tables...")
    #Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")
    
    yield # The application runs here
    
    # This will print when the application shuts down
    await app.state.httpx_client.aclose()
    print("--- FirePulse+ API shutting down. HTTP client closed. ---")

# Initialize the FastAPI application with the lifespan manager
app = FastAPI(
    title="FirePulse+ API",
    description="The backend API for the FirePulse+ social entertainment hub.",
    version="1.0.0",
    lifespan=lifespan
)

# --- THIS IS THE FIX: Add CORSMiddleware ---
# This must be placed before the routers are included.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # The origin of your React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)



app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# --- Include all routers ---
# Routers are included with a prefix and tags for Swagger UI organization.
app.include_router(general_router, prefix="/api/v1", tags=["Main Bot"])
app.include_router(time_routes.router, prefix="/api/v1", tags=["Time-Based Suggestions"])
app.include_router(history_routes.router, prefix="/api/v1", tags=["User History & Recommendations"])
app.include_router(trivia_routes.router, prefix="/api/v1", tags=["Trivia & Gamification"])
app.include_router(auth_routes.router, prefix="/api/v1")
app.include_router(watch_party_routes.router, prefix="/api/v1", tags=["Watch Party"])

# Serve Static Files
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Root Endpoint for a simple health check
@app.get("/", tags=["Root"])
async def read_root():
    """
    Returns a simple status message to indicate the API is running.
    """
    return {"status": "ok", "message": "Welcome to the FirePulse+ API!"}
