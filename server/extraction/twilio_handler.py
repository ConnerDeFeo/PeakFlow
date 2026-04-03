from fastapi import APIRouter, Response
from twilio.twiml.voice_response import VoiceResponse, Connect, ConversationRelay

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/incoming-call")
def incoming_call():
    response = VoiceResponse()
    connect = Connect()
    conversationrelay = ConversationRelay(
        url="wss://receptionist.connerdefeo.com/ws",
        welcome_greeting="Hi, this is Rochester Pro Roofing, our receptionist is currently unavailable, I'm our AI assistant. How can I help you today?",
        interruptible = False
    )
    conversationrelay.language(
        code="en-US",
        tts_provider="ElevenLabs",
        voice="7EzWGsX10sAS4c9m9cPf",
    )
    connect.append(conversationrelay)
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")