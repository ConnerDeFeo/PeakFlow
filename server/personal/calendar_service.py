# calendar_service.py
from datetime import datetime, timedelta
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
    service = get_calendar_service()
    
    events_result = service.events().list(
        calendarId="primary",
        singleEvents=True,
        orderBy="startTime",
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat()
    ).execute()
    
    events = events_result.get("items", [])
    taken = {}
    avail = {}
    for event in events:
        start = event.get("start").get("dateTime").split("T")
        end = event.get("end").get("dateTime").split("T")
        date = start[0]

        if date not in taken:
            taken[date] = []
            avail[date] = []
        
        taken[date].append({
            "start": start[1].split('-')[0],
            "end": end[1].split('-')[0]
        })

        start = datetime.strptime("09:00", "%H:%M")
        end = datetime.strptime("21:00", "%H:%M")

        current = start
        # For each possible time slot, check if it overlaps with any existing events
        while current <= end:
            slot_start = current.time()
            slot_end = (current + timedelta(minutes=30)).time()
            overlap = False
            for event in taken.get(date, []):
                event_start = datetime.strptime(event["start"], "%H:%M:%S").time()
                event_end = datetime.strptime(event["end"], "%H:%M:%S").time()
                if (slot_start < event_end and slot_end > event_start):
                    overlap = True
                    break
            if not overlap:
                avail[date].append({
                    "start": slot_start.strftime("%H:%M:%S"),
                    "end": slot_end.strftime("%H:%M:%S")
                })

            current += timedelta(minutes=30)

    return avail

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