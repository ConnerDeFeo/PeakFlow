# calendar_service.py
from datetime import datetime, time, timedelta
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

def get_available_slots(busy_blocks: list, date: str, slot_duration=30, start_hour=9, end_hour=21):
    available = []
    current = datetime.combine(datetime.fromisoformat(date), time(start_hour, 0))
    end_of_day = datetime.combine(datetime.fromisoformat(date), time(end_hour, 0))

    busy_ranges = [
        (
            datetime.combine(datetime.fromisoformat(date), datetime.strptime(b["start"], "%H:%M:%S").time()),
            datetime.combine(datetime.fromisoformat(date), datetime.strptime(b["end"], "%H:%M:%S").time()),
        )
        for b in busy_blocks
    ]

    while current + timedelta(minutes=slot_duration) <= end_of_day:
        slot_end = current + timedelta(minutes=slot_duration)
        conflict = any(s < slot_end and e > current for s, e in busy_ranges)
        if not conflict:
            available.append(current.strftime("%-I:%M %p"))
        current += timedelta(minutes=slot_duration)

    return available

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