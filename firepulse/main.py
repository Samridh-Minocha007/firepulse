from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import httpx
from contextlib import asynccontextmanager

# --- Import all of your API routers using relative imports ---
# Since main.py is now inside the 'firepulse' package,
# and api is a sibling package, we use '.' for relative import.
from .api.routes import router as general_router
from .api import time_routes
from .api import trivia_routes
from .api import history_routes

# Lifespan manager to create and manage a single, shared httpx client
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This will print when the application starts
    print("--- FirePulse+ API starting. HTTP client created. ---")
    app.state.httpx_client = httpx.AsyncClient(timeout=30.0)
    yield
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

# --- Include all routers ---
# Routers are included with a prefix and tags for Swagger UI organization.
app.include_router(general_router, prefix="/api/v1", tags=["Main Bot"])
app.include_router(time_routes.router, prefix="/api/v1", tags=["Time-Based Suggestions"])
app.include_router(history_routes.router, prefix="/api/v1", tags=["User History & Recommendations"])
app.include_router(trivia_routes.router, prefix="/api/v1", tags=["Trivia & Gamification"])

# Serve Static Files
# The 'static' folder is now directly in the project root (sibling to 'firepulse' package).
# So, the directory path for StaticFiles should be "static".
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Root Endpoint for a simple health check
@app.get("/", tags=["Root"])
async def read_root():
    """
    Returns a simple status message to indicate the API is running.
    """
    return {"status": "ok", "message": "Welcome to the FirePulse+ API!"}

