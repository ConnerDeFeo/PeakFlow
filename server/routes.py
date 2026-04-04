import logging
from fastapi import APIRouter, WebSocket
from config import INCOMING_CALL, WS, Client, SERVER_DOMAIN
from incoming_call_handler import incoming_call
from websocket_handler import websocket_handler

router = APIRouter()
logger = logging.getLogger(__name__)

# Personal routes
@router.post(f"/{Client.PERSONAL}/{INCOMING_CALL}")
def incoming_call_route_personal():
    return incoming_call(
        websocket_url=f"wss://{SERVER_DOMAIN}/{Client.PERSONAL}/{WS}",
        welcome_greeting="Hi, this is Conner DeFeo, our receptionist is currently unavailable, I'm our AI assistant. How can I help you today?",
        voice_name="7EzWGsX10sAS4c9m9cPf"
    )

@router.websocket(f"/{Client.PERSONAL}/{WS}")
async def websocket_route_personal(websocket: WebSocket):
    logger.info("WebSocket connection established for Personal")
    await websocket_handler(websocket, Client.PERSONAL)

# Roofing Rochester routes
@router.post(f"/{Client.ROOFING_ROCHESTER}/{INCOMING_CALL}")
def incoming_call_route_roofing_rochester():
    logger.info("Received incoming call for Roofing Rochester")
    return incoming_call(
        websocket_url=f"wss://{SERVER_DOMAIN}/{Client.ROOFING_ROCHESTER}/{WS}",
        welcome_greeting="Hi, this is Roofing Rochester, our receptionist is currently unavailable, I'm our AI assistant. How can I help you today?",
        voice_name="7EzWGsX10sAS4c9m9cPf"
    )

@router.websocket(f"/{Client.ROOFING_ROCHESTER}/{WS}")
async def websocket_route_roofing_rochester(websocket: WebSocket):
    logger.info("WebSocket connection established for Roofing Rochester")
    await websocket_handler(websocket, Client.ROOFING_ROCHESTER)