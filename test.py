import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.spotify_helper import get_spotify_token

token = get_spotify_token()
print("Token:", token)
