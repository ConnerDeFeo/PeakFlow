import logging
from fastapi import APIRouter, WebSocket
from config import INCOMING_CALL, WS, Client, SERVER_DOMAIN
from incoming_call_handler import incoming_call
from websocket_handler import websocket_handler

router = APIRouter()
logger = logging.getLogger(__name__)

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

# Demo Appointments routes
@router.post(f"/{Client.DEMO.value}/{INCOMING_CALL}/{{company_name}}/{{owner_name}}/{{start_time}}/{{end_time}}/{{days_open}}/{{founded_year}}")
def incoming_call_route_demo_appointments(company_name: str, owner_name: str, start_time: str, end_time: str, days_open: str, founded_year: str):
    formated_company_name = " ".join(company_name.split('_'))
    return incoming_call(
        websocket_url=f"wss://{SERVER_DOMAIN}/{Client.DEMO.value}/{WS}/{company_name}/{owner_name}/{start_time}/{end_time}/{days_open}/{founded_year}",
        welcome_greeting=f"Hi, this is {formated_company_name}, our receptionist is currently unavailable, I'm our AI assistant. How can I help you today?",
        voice_name="7EzWGsX10sAS4c9m9cPf"
    )

@router.websocket(f"/{Client.DEMO.value}/{WS}/{{company_name}}/{{owner_name}}/{{start_time}}/{{end_time}}/{{days_open}}/{{founded_year}}")
async def websocket_route_demo_appointments(websocket: WebSocket, company_name: str, owner_name: str, start_time: str, end_time: str, days_open: str, founded_year: str):
    await websocket_handler(websocket, Client.DEMO, company_name=" ".join(company_name.split('_')), owner_name=" ".join(owner_name.split('_')), start_time=start_time, end_time=end_time, days_open=days_open, founded_year=founded_year)