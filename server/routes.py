import logging
from fastapi import APIRouter, Response, WebSocket
from config import SERVER_URL, Client
from server.incoming_call_handler import incoming_call
from server.websocket_handler import websocket_handler

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/incoming-call")
def incoming_call_route():
    return incoming_call(
        websocket_url=f"{SERVER_URL}/ws",
        welcome_greeting="Hi, this is Rochester Pro Roofing, our receptionist is currently unavailable, I'm our AI assistant. How can I help you today?",
        voice_name="7EzWGsX10sAS4c9m9cPf"
    )

@router.websocket("/ws")
async def websocket_route_roofing_rochester(websocket: WebSocket):
    return websocket_handler(websocket, Client.ROOFING_ROCHESTER)