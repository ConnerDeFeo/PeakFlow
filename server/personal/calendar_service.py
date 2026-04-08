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
    """Return free time blocks between 09:00–21:00 for each date in the range.

    Returns:
        dict[str, list[dict]]: {"YYYY-MM-DD": [{"start": "9:00am", "end": "3:00pm"}, ...]}
    """
    service = get_calendar_service()

    events_result = service.events().list(
        calendarId="primary",
        singleEvents=True,
        orderBy="startTime",
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat()
    ).execute()

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

    def to_12hr(t):
        h, m = t.hour, t.minute
        suffix = "am" if h < 12 else "pm"
        h = h % 12 or 12
        return f"{h}:{m:02d}{suffix}" if m else f"{h}{suffix}"

    avail = {}
    current_date = time_min.date()
    end_date = time_max.date()

    while current_date <= end_date:
        busy = sorted(taken.get(current_date, []))
        
        # Build list of free 30-min slots first
        free_slots = []
        current = datetime.combine(current_date, time(9, 0))
        while current.time() < time(21, 0):
            slot_start = current.time()
            slot_end = (current + timedelta(minutes=30)).time()
            if not any(slot_start < e and slot_end > s for s, e in busy):
                free_slots.append((slot_start, slot_end))
            current += timedelta(minutes=30)

        # Merge consecutive slots into blocks
        blocks = []
        if free_slots:
            block_start, block_end = free_slots[0]
            for slot_start, slot_end in free_slots[1:]:
                if slot_start == block_end:
                    block_end = slot_end
                else:
                    blocks.append({"start": to_12hr(block_start), "end": to_12hr(block_end)})
                    block_start, block_end = slot_start, slot_end
            blocks.append({"start": to_12hr(block_start), "end": to_12hr(block_end)})

        avail[str(current_date)] = blocks
        current_date += timedelta(days=1)

    return avail


def book_google_calendar_appointment(dt, summary, duration_minutes=30, description=""):
    service = get_calendar_service()
    end_dt = dt + timedelta(minutes=duration_minutes)
    
    event = {
        "summary": summary,
        "description": description,
        "colorId": "2",
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