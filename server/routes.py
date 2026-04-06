from datetime import timedelta
import logging
from fastapi import APIRouter, WebSocket
from config import INCOMING_CALL, WS, Client, SERVER_DOMAIN
from incoming_call_handler import incoming_call
from personal.calendar_service import get_available_time_slots
from websocket_handler import websocket_handler
from dateservice import get_current_date

router = APIRouter()
logger = logging.getLogger(__name__)

# Google Calendar routes
@router.get("/test-calendar")
async def test_calendar():
    current_date = get_current_date()
    start = (current_date + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    one_week = start + timedelta(weeks=1)
    available_dates = get_available_time_slots(start, one_week)
    
    return {
        "events": available_dates
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
    current_date = get_current_date()
    start = (current_date + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    one_week = start + timedelta(weeks=1)
    available_time_slots = get_available_time_slots(start, one_week)
    await websocket_handler(websocket, Client.PERSONAL, current_date=current_date, available_time_slots=available_time_slots)

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