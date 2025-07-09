from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
import httpx
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from mangum import Mangum


from .core.db import Base, engine
from .models import user  


from .api.routes import router as general_router
from .api import time_routes
from .api import trivia_routes
from .api import history_routes
from .api import auth_routes
from .api import watch_party_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    print("--- FirePulse+ API starting. HTTP client created. ---")
    app.state.httpx_client = httpx.AsyncClient(timeout=30.0)
    
    
    print("Creating database tables...")
    
    print("Database tables created successfully.")
    
    yield 
    
   
    await app.state.httpx_client.aclose()
    print("--- FirePulse+ API shutting down. HTTP client closed. ---")


app = FastAPI(
    title="FirePulse+ API",
    description="The backend API for the FirePulse+ social entertainment hub.",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)



app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


app.include_router(general_router, prefix="/api/v1", tags=["Main Bot"])
app.include_router(time_routes.router, prefix="/api/v1", tags=["Time-Based Suggestions"])
app.include_router(history_routes.router, prefix="/api/v1", tags=["User History & Recommendations"])
app.include_router(trivia_routes.router, prefix="/api/v1", tags=["Trivia & Gamification"])
app.include_router(auth_routes.router, prefix="/api/v1")
app.include_router(watch_party_routes.router, prefix="/api/v1", tags=["Watch Party"])


if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Root"])
async def read_root():
    
    return {"status": "ok", "message": "Welcome to the FirePulse+ API!"}

handler = Mangum(app)