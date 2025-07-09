import httpx
import base64
from typing import Optional
from fastapi import Request

from ..core.config import settings

async def get_spotify_token(request: Request) -> Optional[str]:
    """
    Asynchronously gets a Spotify API access token.
    It intelligently caches the token in the app's state to avoid refetching on every call.
    """
    client: httpx.AsyncClient = request.app.state.httpx_client
    
   
    if hasattr(request.app.state, "spotify_token") and request.app.state.spotify_token:
        return request.app.state.spotify_token

    
    url = "https://accounts.spotify.com/api/token"
    
    
    auth_string = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    try:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status() 
        
        token = response.json().get("access_token")
        
        
        request.app.state.spotify_token = token
        
        print("✅ Successfully fetched and cached new Spotify token.")
        return token
        
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"❌ Error getting Spotify token: {e}")
        
        if hasattr(request.app.state, "spotify_token"):
            del request.app.state.spotify_token
        return None
