# firepulse/services/google_auth.py
import os
from google_auth_oauthlib.flow import Flow
from ..core.config import settings
import json # <-- NEW IMPORT
from google.oauth2.credentials import Credentials # <-- NEW IMPORT
from googleapiclient.discovery import build # <-- NEW IMPORT

# --- THIS IS THE FIX for InsecureTransportError ---
# This line allows OAuth2 to be used over HTTP for local development.
# It should be removed in a production environment running on HTTPS.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


def get_google_auth_flow():
    """
    Initializes and returns a Google OAuth Flow object using client config.
    """
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
        }
    }

    flow = Flow.from_client_config(
        client_config=client_config,
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/calendar.readonly"
        ],
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )

    return flow

def build_calendar_service(creds_json: str):
    """
    Builds a Google Calendar API service object from stored JSON credentials.
    """
    try:
        # Load the credentials from the JSON string stored in the database
        creds = Credentials.from_authorized_user_info(json.loads(creds_json))

        # Build the service object
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building calendar service: {e}")
        return None
