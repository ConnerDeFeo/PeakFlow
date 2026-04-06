from datetime import datetime, timezone
import logging
from fastapi import APIRouter, WebSocket
from config import INCOMING_CALL, WS, Client, SERVER_DOMAIN
from incoming_call_handler import incoming_call
from personal.calendar_service import get_calendar_service
from websocket_handler import websocket_handler

router = APIRouter()
logger = logging.getLogger(__name__)

# Google Calendar routes
@router.get("/test-calendar")
async def test_calendar():
    service = get_calendar_service()
    
    events_result = service.events().list(
        calendarId="primary",
        maxResults=10,
        singleEvents=True,
        orderBy="startTime",
        timeMin=datetime.now(timezone.utc).isoformat()
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

# Personal routes
@router.post(f"/{Client.PERSONAL.value}/{INCOMING_CALL}")
def incoming_call_route_personal():
    return incoming_call(
        websocket_url=f"wss://{SERVER_DOMAIN}/{Client.PERSONAL.value}/{WS}",
        welcome_greeting="Hello! I am an AI receptionist, how can I assist you today?",
        voice_name="gfRt6Z3Z8aTbpLfexQ7N"
    )

@router.websocket(f"/{Client.PERSONAL.value}/{WS}")
async def websocket_route_personal(websocket: WebSocket):
    await websocket_handler(websocket, Client.PERSONAL)

# Roofing Rochester routes
@router.post(f"/{Client.ROOFING_ROCHESTER.value}/{INCOMING_CALL}")
def incoming_call_route_roofing_rochester():
    return incoming_call(
        websocket_url=f"wss://{SERVER_DOMAIN}/{Client.ROOFING_ROCHESTER.value}/{WS}",
        welcome_greeting="Hi, this is Roofing Rochester, our receptionist is currently unavailable, I'm our AI assistant. How can I help you today?",
        voice_name="7EzWGsX10sAS4c9m9cPf"
    )

@router.websocket(f"/{Client.ROOFING_ROCHESTER.value}/{WS}")
async def websocket_route_roofing_rochester(websocket: WebSocket):
    await websocket_handler(websocket, Client.ROOFING_ROCHESTER)