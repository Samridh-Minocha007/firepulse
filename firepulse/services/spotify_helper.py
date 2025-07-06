import httpx
import base64
from typing import Optional
from fastapi import Request
from ..core.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

async def get_spotify_token(request: Request) -> Optional[str]:
    """
    Asynchronously gets a Spotify API access token.
    It intelligently caches the token in the app's state to avoid refetching on every call.
    """
    client: httpx.AsyncClient = request.app.state.httpx_client
    
    # Check if a valid token is already cached in the app state
    # In a production app, you would also check if the token is expired here
    if hasattr(request.app.state, "spotify_token") and request.app.state.spotify_token:
        return request.app.state.spotify_token

    # If no token is cached, request a new one
    url = "https://accounts.spotify.com/api/token"
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    try:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status() # Raise an exception for bad status codes
        
        token = response.json().get("access_token")
        
        # Cache the new token in the app state for other requests to use
        request.app.state.spotify_token = token
        
        print("✅ Successfully fetched and cached new Spotify token.")
        return token
        
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        print(f"❌ Error getting Spotify token: {e}")
        # Clear the cached token on failure
        if hasattr(request.app.state, "spotify_token"):
            del request.app.state.spotify_token
        return None