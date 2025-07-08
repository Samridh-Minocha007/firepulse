# firepulse/api/auth_routes.py
from fastapi import APIRouter, Depends, HTTPException, status,Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from jose import JWTError, jwt
from typing import List

# --- MODIFIED: Use specific imports to fix the AttributeError ---
from ..schemas import user as user_schema,trivia as trivia_schema
from ..crud import user as user_crud
from ..core import security
from ..core.db import SessionLocal
from ..core.config import settings
from ..models.user import User as UserModel

# Import google_auth module (adjust the import path as needed)
from ..services import google_auth

router = APIRouter()

# This tells FastAPI what URL to check for the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- NEW: Dependency to get the current user from a token ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = user_crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# --- MODIFIED: Endpoint to start the Google login flow ---
@router.get("/login/google", tags=["Authentication"])
def google_login(request: Request): # Add Request to the function signature
    """
    Generates a URL to the Google login page and redirects the user there.
    """
    flow = google_auth.get_google_auth_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    # --- FIX: Store the state in the session ---
    request.session['state'] = state

    return RedirectResponse(authorization_url)

# --- MODIFIED: Endpoint to handle the callback from Google ---
@router.get("/auth/callback", tags=["Authentication"])
def auth_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handles the redirect from Google after user authentication.
    """
    # --- FIX: Retrieve state from session and validate ---
    state = request.session.get('state')
    if not state:
        raise HTTPException(status_code=400, detail="State not found in session.")

    flow = google_auth.get_google_auth_flow()

    flow.fetch_token(
        authorization_response=str(request.url),
        state=state # Pass the state for validation
    )

    credentials = flow.credentials

    user_info = jwt.get_unverified_claims(credentials.id_token)
    user_email = user_info.get("email")

    db_user = user_crud.get_user_by_email(db, email=user_email)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail=f"User with email {user_email} not found. Please register first."
        )

    user_crud.update_user_google_creds(db, user_email=user_email, creds_json=credentials.to_json())

    return {"status": "ok", "message": f"Successfully linked Google account for {user_email}"}

@router.get("/calendar/events/", tags=["Calendar"])
def get_calendar_events(current_user: UserModel = Depends(get_current_user)):
    """
    Fetches upcoming calendar events for the logged-in user.
    The user must have already linked their Google account.
    """
    if not current_user.google_creds_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account not linked. Please go through the Google login flow first."
        )

    service = google_auth.build_calendar_service(current_user.google_creds_json)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create Google Calendar service."
        )

    try:
        # Get the start of today and the end of the next 7 days
        now = datetime.now(timezone.utc).isoformat()
        end_time = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

        events_result = service.events().list(
            calendarId='primary', 
            timeMin=now,
            timeMax=end_time,
            maxResults=10, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return {"message": "No upcoming events found."}

        # Format the events for the response
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            formatted_events.append({
                "summary": event['summary'],
                "start": start
            })

        return formatted_events

    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching calendar events."
        )

@router.post("/users/", response_model=user_schema.User, tags=["Authentication"])
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create_user(db=db, user=user)


@router.post("/token", response_model=user_schema.Token, tags=["Authentication"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs in a user and returns a JWT access token."""
    user = user_crud.get_user_by_email(db, email=form_data.username) 
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- NEW: Protected endpoint to get the current user's info ---
@router.get("/users/me/", response_model=user_schema.User, tags=["Authentication"])
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """
    Fetch the currently logged-in user.
    """
    return current_user


# --- NEW: Endpoint to get the current user's badges ---
@router.get("/users/me/badges", response_model=List[trivia_schema.Badge], tags=["Authentication"])
def read_user_badges(current_user: UserModel = Depends(get_current_user)):
    """
    Fetch all badges for the currently logged-in user.
    """
    return current_user.badges