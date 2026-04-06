# calendar_service.py
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "token.json")

def get_calendar_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)
