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
    res = {}
    for event in events:
        start = event.get("start").get("dateTime").split("T")
        end = event.get("end").get("dateTime").split("T")
        date = start[0]

        if date not in res:
            res[date] = []
        
        res[date].append({
            "start": start[1].split('-')[0],
            "end": end[1].split('-')[0]
        })

    return res

def book_google_calendar_appointment(dt, summary, duration_minutes=60, description=""):
    service = get_calendar_service()
    end_dt = dt + timedelta(minutes=duration_minutes)
    
    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": dt.isoformat(),
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "UTC"
        }
    }
    
    created_event = service.events().insert(calendarId="primary", body=event).execute()
    return created_event.get("id")