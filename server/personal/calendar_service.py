# calendar_service.py
from datetime import datetime, timedelta, timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()
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

def get_available_dates(time_min, time_max):
    service = get_calendar_service()
    
    events_result = service.events().list(
        calendarId="primary",
        singleEvents=True,
        orderBy="startTime",
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat()
    ).execute()
    
    events = events_result.get("items", [])
    
    return {
        "events": [
            {
                "summary": e.get("summary"),
                "start": e.get("start"),
                "end": e.get("end"),
            }
            for e in events
        ]
    }
