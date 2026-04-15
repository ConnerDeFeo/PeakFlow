from datetime import timedelta, datetime
import logging
from zoneinfo import ZoneInfo
from fastapi import APIRouter, WebSocket
from config import INCOMING_CALL, WS, Client, SERVER_DOMAIN
from incoming_call_handler import incoming_call
from personal.calendar_service import get_available_time_slots
from websocket_handler import websocket_handler

router = APIRouter()
logger = logging.getLogger(__name__)

# Personal routes
@router.post(f"/{Client.PERSONAL.value}/{INCOMING_CALL}")
def incoming_call_route_personal():
    logger.debug(f"Setting up incoming call route for {Client.PERSONAL.value}")
    return incoming_call(
        websocket_url=f"wss://{SERVER_DOMAIN}/{Client.PERSONAL.value}/{WS}",
        welcome_greeting="Hello! I am an AI receptionist, how can I assist you today?",
        voice_name="gfRt6Z3Z8aTbpLfexQ7N"
    )

@router.websocket(f"/{Client.PERSONAL.value}/{WS}")
async def websocket_route_personal(websocket: WebSocket):
    now = datetime.now(ZoneInfo("America/New_York"))
    current_date = now.strftime("%A, %B %d, %Y %I:%M %p %Z")
    tmr = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    one_week = (now + timedelta(weeks=1, days=1)).replace(hour=21, minute=0, second=0, microsecond=0)
    available_time_slots = get_available_time_slots(tmr, one_week)
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


# Adonis Roofing routes
@router.post(f"/{Client.ADONIS_ROOFING.value}/{INCOMING_CALL}")
def incoming_call_route_adonis_roofing():
    return incoming_call(
        websocket_url=f"wss://{SERVER_DOMAIN}/{Client.ADONIS_ROOFING.value}/{WS}",
        welcome_greeting="Hi, this is Adonis Roofing, our receptionist is currently unavailable, I'm our AI assistant. How can I help you today?",
        voice_name="X03mvPuTfprif8QBAVeJ"
    )

@router.websocket(f"/{Client.ADONIS_ROOFING.value}/{WS}")
async def websocket_route_adonis_roofing(websocket: WebSocket):
    await websocket_handler(websocket, Client.ADONIS_ROOFING)