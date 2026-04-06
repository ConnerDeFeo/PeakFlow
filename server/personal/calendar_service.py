# calendar_service.py
from datetime import datetime, time, timedelta
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH", "token.json")

logger = logging.getLogger(__name__)

def get_calendar_service():
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def get_available_time_slots(time_min, time_max):
    """Return free 30-minute slots between 09:00–21:00 for each date in the range.

    Returns:
        dict[str, list[dict]]: {"YYYY-MM-DD": [{"start": "HH:MM:SS", "end": "HH:MM:SS"}, ...]}
    """
    service = get_calendar_service()

    # Fetch events in the range; singleEvents=True expands recurring events into instances
    events_result = service.events().list(
        calendarId="primary",
        singleEvents=True,
        orderBy="startTime",
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat()
    ).execute()

    # Pass 1: group busy (start, end) time pairs by date.
    # Events without a dateTime (i.e. all-day events) are skipped.
    taken = {}
    for event in events_result.get("items", []):
        start = event.get("start", {}).get("dateTime")
        end = event.get("end", {}).get("dateTime")
        if not start or not end:
            continue
        start_dt = datetime.fromisoformat(start).replace(tzinfo=None)
        end_dt = datetime.fromisoformat(end).replace(tzinfo=None)
        date = start_dt.date()
        taken.setdefault(date, []).append((start_dt.time(), end_dt.time()))

    # Pass 2: for each date, walk 09:00–21:00 in 30-minute steps and keep
    # any slot that doesn't overlap a busy block. Overlap condition:
    # slot starts before the block ends AND slot ends after the block starts.
    avail = {}
    for date, busy in taken.items():
        slots = []
        current = datetime.combine(date, time(9, 0))
        while current.time() <= time(21, 0):
            slot_start = current.time()
            slot_end = (current + timedelta(minutes=30)).time()
            if not any(slot_start < e and slot_end > s for s, e in busy):
                slots.append({"start": str(slot_start), "end": str(slot_end)})
            current += timedelta(minutes=30)
        avail[str(date)] = slots

    return avail, taken


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