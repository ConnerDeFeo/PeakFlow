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


def book_appointment(
    summary: str,
    start_time: datetime,
    duration_minutes: int = 60,
    description: str = "",
    attendee_email: str = None,
) -> dict:
    service = get_calendar_service()
    
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "America/New_York"},
        "end":   {"dateTime": end_time.isoformat(),   "timeZone": "America/New_York"},
    }
    
    if attendee_email:
        event["attendees"] = [{"email": attendee_email}]
    
    result = service.events().insert(calendarId="primary", body=event).execute()
    return result


def get_available_slots(
    date: datetime,
    duration_minutes: int = 60,
    start_hour: int = 8,
    end_hour: int = 17,
) -> list[dict]:
    """Returns free slots on a given day."""
    service = get_calendar_service()
    
    day_start = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    day_end   = date.replace(hour=end_hour,   minute=0, second=0, microsecond=0)
    
    # Get busy times via freebusy query
    body = {
        "timeMin": day_start.isoformat() + "Z",
        "timeMax": day_end.isoformat() + "Z",
        "items": [{"id": "primary"}],
    }
    freebusy = service.freebusy().query(body=body).execute()
    busy_periods = freebusy["calendars"]["primary"]["busy"]
    
    # Build free slots
    free_slots = []
    current = day_start
    delta = timedelta(minutes=duration_minutes)
    
    while current + delta <= day_end:
        slot_end = current + delta
        is_free = all(
            slot_end <= datetime.fromisoformat(b["start"].replace("Z", ""))
            or current >= datetime.fromisoformat(b["end"].replace("Z", ""))
            for b in busy_periods
        )
        if is_free:
            free_slots.append({"start": current.isoformat(), "end": slot_end.isoformat()})
        current += timedelta(minutes=30)  # 30-min increments
    
    return free_slots